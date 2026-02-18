import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { spawn } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { v4 as uuidv4 } from 'uuid';
import { PrismaService } from '../prisma/prisma.service.js';
import {
  DockerExecutorService,
  ExecutionResult,
} from './docker-executor.service.js';
import { Judge0Service } from './judge0.service.js';

function toPositiveInt(value: string): number | null {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed <= 0) return null;
  return parsed;
}

@Injectable()
export class ExecuteService {
  private readonly logger = new Logger(ExecuteService.name);
  private useDocker: boolean;
  private useJudge0: boolean;
  private questionsDir: string;
  private timeout: number;

  constructor(
    private readonly prisma: PrismaService,
    private readonly config: ConfigService,
    private readonly dockerExecutor: DockerExecutorService,
    private readonly judge0Service: Judge0Service,
  ) {
    this.useDocker = this.config.get<boolean>('docker.useDocker')!;
    this.useJudge0 = this.config.get<boolean>('judge0.enabled') ?? false;
    this.questionsDir = this.config.get<string>('questionsDir')!;
    this.timeout = this.config.get<number>('docker.timeout')!;

    if (this.useDocker && !this.dockerExecutor.isAvailable()) {
      console.warn(
        'Docker execution requested but Docker is not available. Falling back to local execution.',
      );
    }
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
    const { imageName, envVars, networkEnabled, errorResult } =
      await this.resolveExecutionConfig(moduleId, currentUser);
    if (errorResult) return errorResult;

    // Judge0 Execution
    if (this.useJudge0 && this.judge0Service.isAvailable()) {
      let finalCode = code;
      const dataCsvPath = path.join(folderPath, 'data.csv');

      // If data.csv exists, bundle it into the python script
      if (fs.existsSync(dataCsvPath)) {
        try {
          // Escape triple quotes in CSV content to avoid syntax errors if any
          const csvContent = fs.readFileSync(dataCsvPath, 'utf-8').replace(/'''/g, "\\'\\'\\'");
          const setupCode = `
import os
if not os.path.exists('data.csv'):
    with open('data.csv', 'w') as f:
        f.write('''${csvContent}''')
`;
          finalCode = setupCode + '\n' + code;
        } catch (e) {
          console.error('Error bundling data.csv for Judge0:', e);
        }
      }

      const judge0Result = await this.judge0Service.runCode(finalCode);
      if (!this.shouldFallbackFromJudge0(judge0Result)) {
        return judge0Result;
      }

      this.logger.warn(
        'Judge0 runtime environment error detected; falling back to Docker/local executor.',
      );
    }

    if (this.useDocker && this.dockerExecutor.isAvailable()) {
      return this.dockerExecutor.runCode(
        code,
        folderPath,
        imageName,
        envVars,
        networkEnabled,
      );
    }

    return this.runLocal(code, folderPath, envVars, false);
  }

  private shouldFallbackFromJudge0(result: ExecutionResult): boolean {
    if (result.status === 'success') return false;

    const stderr = (result.stderr || '').toLowerCase();
    return (
      stderr.includes('rosetta error') ||
      stderr.includes('caught fatal signal 5') ||
      stderr.includes('/box/script.py') ||
      stderr.includes('execution environment error')
    );
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
    const { imageName, envVars, networkEnabled, errorResult } =
      await this.resolveExecutionConfig(moduleId, currentUser);
    if (errorResult) return errorResult;

    if (this.useDocker && this.dockerExecutor.isAvailable()) {
      return this.dockerExecutor.validateCode(
        code,
        folderPath,
        imageName,
        envVars,
        networkEnabled,
      );
    }

    return this.runLocal(code, folderPath, envVars, true);
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
    let imageName = 'practice-room-python:latest';
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
      const mod = await this.prisma.module.findUnique({
        where: { id: parsedModuleId },
      });
      // if (mod?.base_image) imageName = mod.base_image;
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

  private runLocal(
    code: string,
    questionFolderPath: string,
    envVars: Record<string, string>,
    isValidation: boolean,
  ): Promise<ExecutionResult> {
    return new Promise((resolve) => {
      const runId = uuidv4();
      const runsDir = this.dockerExecutor.getRunsDir();
      const workDir = path.join(runsDir, runId);
      fs.mkdirSync(workDir, { recursive: true });

      try {
        // Write user code
        fs.writeFileSync(path.join(workDir, 'user_code.py'), code, 'utf-8');

        // Copy data files
        if (fs.existsSync(questionFolderPath)) {
          for (const f of fs.readdirSync(questionFolderPath)) {
            if (
              (f.endsWith('.csv') ||
                f.endsWith('.txt') ||
                f.endsWith('.json') ||
                f.endsWith('.py')) &&
              f !== 'master_question_list.csv'
            ) {
              fs.copyFileSync(
                path.join(questionFolderPath, f),
                path.join(workDir, f),
              );
            }
          }
        }

        // Copy _env.py
        const envFile = path.join(this.questionsDir, '_env.py');
        if (fs.existsSync(envFile)) {
          fs.copyFileSync(envFile, path.join(workDir, '_env.py'));
        }

        // Write driver
        const driverFile = isValidation
          ? 'validate_driver.py'
          : 'main.py';
        const driverCode = isValidation
          ? `
import sys, os, builtins, pandas as pd, warnings
warnings.simplefilter("ignore")
sys.path.append(os.getcwd())
if os.path.exists("data.csv"):
    try:
        loaded_df = pd.read_csv("data.csv")
        loaded_df.columns = loaded_df.columns.str.lower().str.strip()
        builtins.data = loaded_df
        builtins.df = loaded_df
    except: pass
try:
    from _env import get_llm
    builtins.get_llm = get_llm
except: pass
import validator, user_code
try:
    result = validator.validate(user_code)
    print(result)
except Exception as e:
    print(f"Validation Wrapper Error: {e}")
`
          : `
import sys, os, traceback, warnings
warnings.simplefilter("ignore")
sys.path.append(os.getcwd())

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

try:
    import pandas as pd
    HAS_PD = True
except ImportError:
    HAS_PD = False

global_ns = {"__name__": "__main__", "__file__": "user_code.py"}
try:
    if HAS_PD and os.path.exists("data.csv"):
        try:
            loaded_df = pd.read_csv("data.csv")
            loaded_df.columns = loaded_df.columns.str.lower().str.strip()
            global_ns["data"] = loaded_df
            global_ns["df"] = loaded_df
        except: pass
    try:
        from _env import get_llm
        import builtins
        builtins.get_llm = get_llm
        global_ns["get_llm"] = get_llm
    except: pass
    with open("user_code.py", "r", encoding="utf-8") as f:
        user_source = f.read()
    exec(user_source, global_ns)
    if HAS_MPL:
        fignums = plt.get_fignums()
        if fignums:
            for i, num in enumerate(fignums):
                fig = plt.figure(num)
                fname = "output.png" if len(fignums) == 1 else f"output_{i+1}.png"
                fig.savefig(fname, bbox_inches='tight')
                plt.close(fig)
except Exception as e:
    traceback.print_exc()
`;
        fs.writeFileSync(
          path.join(workDir, driverFile),
          driverCode,
          'utf-8',
        );

        // Spawn Python process
        const env = { ...process.env, PYTHONIOENCODING: 'utf-8', ...envVars };
        const proc = spawn('python3', [driverFile], {
          cwd: workDir,
          env,
          timeout: this.timeout * 1000,
        });

        let stdout = '';
        let stderr = '';

        proc.stdout.on('data', (data: Buffer) => {
          stdout += data.toString('utf-8');
        });
        proc.stderr.on('data', (data: Buffer) => {
          stderr += data.toString('utf-8');
        });

        proc.on('close', (exitCode: number | null) => {
          // Collect artifacts
          const artifacts: string[] = [];
          if (fs.existsSync(workDir)) {
            for (const f of fs.readdirSync(workDir)) {
              if (f.startsWith('output') && f.endsWith('.png')) {
                artifacts.push(f);
              }
            }
            artifacts.sort();
          }

          // Truncate
          const MAX = 50000;
          if (stdout.length > MAX)
            stdout =
              stdout.substring(0, MAX) +
              '\n... [Output truncated]';
          if (stderr.length > MAX)
            stderr =
              stderr.substring(0, MAX) +
              '\n... [Error output truncated]';

          resolve({
            stdout,
            stderr,
            artifacts,
            status: exitCode === 0 ? 'success' : 'error',
            run_id: runId,
          });
        });

        proc.on('error', (err: Error) => {
          resolve({
            stdout: '',
            stderr: `Execution failed: ${err.message}`,
            artifacts: [],
            status: 'error',
            run_id: runId,
          });
        });
      } catch (e: any) {
        resolve({
          stdout: '',
          stderr: `Backend Execution Error: ${e.message}`,
          artifacts: [],
          status: 'error',
          run_id: runId,
        });
      }
    });
  }
}
