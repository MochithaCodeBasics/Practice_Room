import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../prisma/prisma.service.js';
import { DockerExecutorService, ExecutionResult } from './docker-executor.service.js';
import { Judge0Service } from './judge0.service.js';

function toPositiveInt(value: string): number | null {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed <= 0) return null;
  return parsed;
}

@Injectable()
export class ExecuteService {
  private readonly logger = new Logger(ExecuteService.name);
  private useJudge0: boolean;

  constructor(
    private readonly prisma: PrismaService,
    private readonly config: ConfigService,
    private readonly judge0Service: Judge0Service,
    private readonly dockerExecutor: DockerExecutorService,
  ) {
    this.useJudge0 = this.config.get<boolean>('judge0.enabled') ?? false;
  }

  /**
   * Runs a prepared Python script using whatever execution backend is available.
   * Judge0 is preferred when enabled; Docker executor is the fallback.
   */
  private async executeScript(code: string): Promise<ExecutionResult> {
    if (this.useJudge0 && this.judge0Service.isAvailable()) {
      return this.judge0Service.runCode(code);
    }
    if (this.dockerExecutor.isAvailable()) {
      return this.dockerExecutor.runScript(code, 'practice-room-python:latest');
    }
    return {
      stdout: '',
      stderr: 'Code execution is unavailable. Neither Judge0 nor Docker executor is configured.',
      artifacts: [],
      status: 'error',
    };
  }

  async runCode(
    code: string,
    questionId: string,
    moduleId: string,
    currentUser?: any,
  ): Promise<ExecutionResult> {
    const parsedQuestionId = toPositiveInt(questionId);
    if (!parsedQuestionId) {
      return { stdout: '', stderr: 'Invalid question id', artifacts: [], status: 'error' };
    }

    const question = await this.prisma.moduleQuestion.findUnique({
      where: { id: parsedQuestionId },
    });
    if (!question) {
      return { stdout: '', stderr: 'Question not found', artifacts: [], status: 'error' };
    }

    const { errorResult } = await this.resolveExecutionConfig(moduleId, currentUser);
    if (errorResult) return errorResult;

    const finalCode = this.buildRunScript(code, question.sample_data ?? null);
    return this.executeScript(finalCode);
  }

  async validateCode(
    code: string,
    questionId: string,
    moduleId: string,
    currentUser?: any,
  ): Promise<ExecutionResult> {
    const parsedQuestionId = toPositiveInt(questionId);
    if (!parsedQuestionId) {
      return { stdout: '', stderr: 'Invalid question id', artifacts: [], status: 'error' };
    }

    const question = await this.prisma.moduleQuestion.findUnique({
      where: { id: parsedQuestionId },
    });
    if (!question) {
      return { stdout: '', stderr: 'Question not found', artifacts: [], status: 'error' };
    }

    const { errorResult } = await this.resolveExecutionConfig(moduleId, currentUser);
    if (errorResult) return errorResult;

    // Step 1: Run the user's submitted code
    const userScript = this.buildRunScript(code, question.sample_data ?? null);
    const userResult = await this.executeScript(userScript);

    // Step 2: If user code errored, fail immediately
    if (userResult.status === 'error') {
      return {
        stdout: '[FAIL] Your code raised an error.',
        stderr: userResult.stderr,
        artifacts: [],
        status: 'error',
      };
    }

    // Step 3: If user code produced no output, fail
    const userOutput = userResult.stdout.trim();
    if (!userOutput) {
      return {
        stdout: '[FAIL] Your code did not produce any output.',
        stderr: '',
        artifacts: [],
        status: 'error',
      };
    }

    // Step 4: Run the validator reference solution from DB
    const validatorCode = question.validator_py;
    if (!validatorCode) {
      return {
        stdout: '[FAIL] No validator configured for this question.',
        stderr: '',
        artifacts: [],
        status: 'error',
      };
    }

    const validatorScript = this.buildRunScript(validatorCode, question.sample_data ?? null);
    const validatorResult = await this.executeScript(validatorScript);

    if (validatorResult.status === 'error') {
      this.logger.error(`Validator script failed for question ${parsedQuestionId}: ${validatorResult.stderr}`);
      return {
        stdout: '[FAIL] Validator script error. Please contact support.',
        stderr: validatorResult.stderr,
        artifacts: [],
        status: 'error',
      };
    }

    // Step 5: Compare outputs
    const validatorOutput = validatorResult.stdout.trim();

    if (userOutput === validatorOutput) {
      return { stdout: '[PASS] Correct!', stderr: '', artifacts: [], status: 'success' };
    }

    return {
      stdout: `[FAIL] Output does not match expected.\n\nExpected:\n${validatorOutput}\n\nGot:\n${userOutput}`,
      stderr: '',
      artifacts: [],
      status: 'error',
    };
  }

  /**
   * Wraps user code with a data.csv setup block so `data`/`df` globals are available.
   */
  private buildRunScript(userCode: string, sampleData: string | null): string {
    if (!sampleData) return userCode;
    const csvB64 = Buffer.from(sampleData).toString('base64');
    return `import io as _io, pandas as _pd, base64 as _b64, builtins as _builtins
try:
    _df = _pd.read_csv(_io.StringIO(_b64.b64decode('${csvB64}').decode('utf-8')))
    _df.columns = _df.columns.str.lower().str.strip()
    _builtins.data = _df
    _builtins.df = _df
except Exception:
    pass

${userCode}`;
  }


  private async resolveExecutionConfig(
    moduleId: string,
    currentUser?: any,
  ): Promise<{
    imageName: string;
    envVars: Record<string, string>;
    networkEnabled: boolean;
    errorResult?: ExecutionResult;
  }> {
    const imageName = 'practice-room-python:latest';
    const envVars: Record<string, string> = {};

    if (moduleId) {
      const parsedModuleId = toPositiveInt(moduleId);
      if (!parsedModuleId) {
        return {
          imageName,
          envVars,
          networkEnabled: false,
          errorResult: {
            stdout: '',
            stderr: 'Invalid module id',
            artifacts: [],
            status: 'error',
          },
        };
      }
    }

    if (currentUser) {
      if (currentUser.groq_api_key)
        envVars.GROQ_API_KEY = currentUser.groq_api_key.trim();
      if (currentUser.openai_api_key)
        envVars.OPENAI_API_KEY = currentUser.openai_api_key.trim();
      if (currentUser.anthropic_api_key)
        envVars.ANTHROPIC_API_KEY = currentUser.anthropic_api_key.trim();
      envVars.DEFAULT_LLM_PROVIDER =
        currentUser.default_llm_provider || 'groq';
    }

    const isAiModule = ['genai', 'agentic', 'nlp'].some((kw) =>
      imageName.toLowerCase().includes(kw),
    );
    const networkEnabled = isAiModule;

    if (isAiModule) {
      const hasAnyKey =
        currentUser &&
        (currentUser.groq_api_key ||
          currentUser.openai_api_key ||
          currentUser.anthropic_api_key);
      if (!hasAnyKey) {
        return {
          imageName,
          envVars,
          networkEnabled,
          errorResult: {
            stdout: '',
            stderr:
              'No service keys configured. Please go to Environment Settings and enter a provider key (Groq, OpenAI, or Anthropic) to use advanced features.',
            artifacts: [],
            status: 'error',
          },
        };
      }
    }

    return { imageName, envVars, networkEnabled };
  }

}
