import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { PrismaService } from '../prisma/prisma.service.js';
import { ExecutionResult } from './docker-executor.service.js';
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
  private questionsDir: string;

  constructor(
    private readonly prisma: PrismaService,
    private readonly config: ConfigService,
    private readonly judge0Service: Judge0Service,
  ) {
    this.useJudge0 = this.config.get<boolean>('judge0.enabled') ?? false;
    this.questionsDir = this.config.get<string>('questionsDir')!;
  }

  async runCode(
    code: string,
    questionId: string,
    moduleId: string,
    currentUser?: any,
  ): Promise<ExecutionResult> {
    const parsedQuestionId = toPositiveInt(questionId);
    if (!parsedQuestionId) {
      return {
        stdout: '',
        stderr: 'Invalid question id',
        artifacts: [],
        status: 'error',
      };
    }

    const question = await this.prisma.moduleQuestion.findUnique({
      where: { id: parsedQuestionId },
    });
    if (!question) {
      return {
        stdout: '',
        stderr: 'Question not found',
        artifacts: [],
        status: 'error',
      };
    }

    const folderPath = this.ensureQuestionWorkspace(question);
    const { errorResult } = await this.resolveExecutionConfig(moduleId, currentUser);
    if (errorResult) return errorResult;

    if (!this.useJudge0 || !this.judge0Service.isAvailable()) {
      return {
        stdout: '',
        stderr: 'Code execution is unavailable. Judge0 is not configured or unreachable.',
        artifacts: [],
        status: 'error',
      };
    }

    let finalCode = code;
    const dataCsvPath = path.join(folderPath, 'data.csv');

    if (fs.existsSync(dataCsvPath)) {
      try {
        const csvContent = fs.readFileSync(dataCsvPath, 'utf-8').replace(/'''/g, "\\'\\'\\'");
        const setupCode = `
import os
if not os.path.exists('data.csv'):
    with open('data.csv', 'w') as f:
        f.write('''${csvContent}''')
`;
        finalCode = setupCode + '\n' + code;
      } catch (e) {
        this.logger.error('Error bundling data.csv for Judge0:', e);
      }
    }

    return this.judge0Service.runCode(finalCode);
  }

  async validateCode(
    code: string,
    questionId: string,
    moduleId: string,
    currentUser?: any,
  ): Promise<ExecutionResult> {
    const parsedQuestionId = toPositiveInt(questionId);
    if (!parsedQuestionId) {
      return {
        stdout: '',
        stderr: 'Invalid question id',
        artifacts: [],
        status: 'error',
      };
    }

    const question = await this.prisma.moduleQuestion.findUnique({
      where: { id: parsedQuestionId },
    });
    if (!question) {
      return {
        stdout: '',
        stderr: 'Question not found',
        artifacts: [],
        status: 'error',
      };
    }

    const folderPath = this.ensureQuestionWorkspace(question);
    const { errorResult } = await this.resolveExecutionConfig(moduleId, currentUser);
    if (errorResult) return errorResult;

    if (!this.useJudge0 || !this.judge0Service.isAvailable()) {
      return {
        stdout: '',
        stderr: 'Code validation is unavailable. Judge0 is not configured or unreachable.',
        artifacts: [],
        status: 'error',
      };
    }

    const combinedScript = this.buildJudge0ValidateScript(code, folderPath);
    return this.judge0Service.runCode(combinedScript);
  }

  /**
   * Builds a self-contained Python script for Judge0 that simulates the
   * local validation environment: embeds data.csv, user code, and validator.py
   * as base64 strings and runs validator.validate(user_code_module).
   */
  private buildJudge0ValidateScript(userCode: string, questionFolderPath: string): string {
    const validatorPath = path.join(questionFolderPath, 'validator.py');
    const validatorCode = fs.existsSync(validatorPath)
      ? fs.readFileSync(validatorPath, 'utf-8')
      : 'def validate(user_code_module):\n    return "[FAIL] validator missing"';

    const dataCsvPath = path.join(questionFolderPath, 'data.csv');
    let csvContent: string | null = null;
    if (fs.existsSync(dataCsvPath)) {
      try {
        csvContent = fs.readFileSync(dataCsvPath, 'utf-8');
      } catch (e) {
        this.logger.error('Error reading data.csv for Judge0 validation:', String(e));
      }
    }

    const userCodeB64 = Buffer.from(userCode).toString('base64');
    const validatorCodeB64 = Buffer.from(validatorCode).toString('base64');

    const csvSetupBlock = csvContent
      ? `
try:
    import io as _io, pandas as _pd, base64 as _b64, builtins as _builtins
    _df = _pd.read_csv(_io.StringIO(_b64.b64decode('${Buffer.from(csvContent).toString('base64')}').decode('utf-8')))
    _df.columns = _df.columns.str.lower().str.strip()
    _builtins.data = _df
    _builtins.df = _df
except Exception:
    pass
`
      : '';

    return `import sys, types, builtins, warnings, base64
warnings.simplefilter("ignore")
${csvSetupBlock}
_user_code = types.ModuleType("user_code")
if hasattr(builtins, "data"):
    _user_code.data = builtins.data
    _user_code.df = builtins.df
exec(base64.b64decode('${userCodeB64}').decode('utf-8'), _user_code.__dict__)
sys.modules["user_code"] = _user_code

_validator = types.ModuleType("validator")
exec(base64.b64decode('${validatorCodeB64}').decode('utf-8'), _validator.__dict__)
sys.modules["validator"] = _validator

try:
    result = _validator.validate(_user_code)
    print(result)
except Exception as e:
    print(f"Validation Wrapper Error: {e}")
`;
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

  private ensureQuestionWorkspace(question: {
    id: number;
    folder_name: string;
    question_py: string | null;
    initial_code: string | null;
    hint: string | null;
    validator_py: string | null;
    sample_data: string | null;
  }): string {
    const diskPath = path.join(this.questionsDir, question.folder_name);
    if (fs.existsSync(diskPath)) {
      return diskPath;
    }

    const fallbackDir = path.join(
      os.tmpdir(),
      'practice-room-db-questions',
      String(question.id),
    );
    fs.mkdirSync(fallbackDir, { recursive: true });

    const questionPyPath = path.join(fallbackDir, 'question.py');
    if (!fs.existsSync(questionPyPath)) {
      const rendered = [
        `description = """\n${question.question_py || ''}\n"""`,
        `initial_sample_code = """\n${question.initial_code || ''}\n"""`,
        `hint = """\n${question.hint || ''}\n"""`,
      ].join('\n\n');
      fs.writeFileSync(questionPyPath, rendered, 'utf-8');
    }

    const validatorPyPath = path.join(fallbackDir, 'validator.py');
    if (!fs.existsSync(validatorPyPath)) {
      fs.writeFileSync(
        validatorPyPath,
        question.validator_py || 'def validate(user_code_module):\n    return "[FAIL] validator missing"',
        'utf-8',
      );
    }

    if (question.sample_data) {
      const sampleDataPath = path.join(fallbackDir, 'data.csv');
      if (!fs.existsSync(sampleDataPath)) {
        fs.writeFileSync(sampleDataPath, question.sample_data, 'utf-8');
      }
    }

    return fallbackDir;
  }
}
