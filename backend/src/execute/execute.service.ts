import { Injectable } from '@nestjs/common';
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

    const validatorCode = question.validator_py;
    if (!validatorCode) {
      return {
        stdout: '[FAIL] No validator configured for this question.',
        stderr: '',
        artifacts: [],
        status: 'error',
      };
    }

    // Build a single combined script: user code + validator run together
    const combinedScript = this.buildValidateScript(code, validatorCode, question.sample_data ?? null);
    const result = await this.executeScript(combinedScript);

    if (result.status === 'error') {
      return {
        stdout: `[FAIL] ${result.stdout || 'Execution error.'}`,
        stderr: result.stderr,
        artifacts: [],
        status: 'error',
      };
    }

    const output = result.stdout.trim();
    const passed = output.includes('[PASS]') || output.includes('Correct!') || output.includes('✅');

    return {
      stdout: passed ? `[PASS] ${output}` : `[FAIL] ${output}`,
      stderr: result.stderr,
      artifacts: [],
      status: passed ? 'success' : 'error',
    };
  }

  /**
   * Builds a combined Python script that runs user code and validator together.
   * The validator's validate(user_module) function is called and its result printed.
   * Both code strings are base64-encoded inside the script to avoid quoting issues.
   */
  private buildValidateScript(userCode: string, validatorCode: string, sampleData: string | null): string {
    const userCodeB64 = Buffer.from(userCode).toString('base64');
    const validatorCodeB64 = Buffer.from(validatorCode).toString('base64');

    const dataSetup = sampleData
      ? `import io as _io, pandas as _pd, builtins as _builtins
try:
    _df = _pd.read_csv(_io.StringIO(_b64.b64decode('${Buffer.from(sampleData).toString('base64')}').decode('utf-8')))
    _df.columns = _df.columns.str.lower().str.strip()
    _builtins.data = _df
    _builtins.df = _df
except Exception:
    pass
`
      : '';

    return `import base64 as _b64, types as _types
${dataSetup}
_user_module = _types.ModuleType("user_code")
exec(_b64.b64decode('${userCodeB64}').decode('utf-8'), _user_module.__dict__)

_validator_module = _types.ModuleType("validator")
exec(_b64.b64decode('${validatorCodeB64}').decode('utf-8'), _validator_module.__dict__)

_result = _validator_module.validate(_user_module)
print(_result)
`;
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
