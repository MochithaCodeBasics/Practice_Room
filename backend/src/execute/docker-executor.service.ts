import { Injectable, OnModuleInit } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import Docker from 'dockerode';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { v4 as uuidv4 } from 'uuid';
import pLimit from 'p-limit';

export interface ExecutionResult {
  stdout: string;
  stderr: string;
  artifacts: string[];
  status: string;
  run_id?: string;
}

// Python driver scripts (executed inside the container)
const RUN_DRIVER = `
import sys
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import traceback
import warnings

warnings.simplefilter("ignore")
sys.path.append(os.getcwd())

global_ns = {
    "__name__": "__main__",
    "__file__": "user_code.py"
}

try:
    if os.path.exists("data.csv"):
        try:
            loaded_df = pd.read_csv("data.csv")
            loaded_df.columns = loaded_df.columns.str.lower().str.strip()
            global_ns["data"] = loaded_df
            global_ns["df"] = loaded_df
        except Exception:
            pass

    try:
        from _env import get_llm
        import builtins
        builtins.get_llm = get_llm
        global_ns["get_llm"] = get_llm
    except Exception:
        pass

    with open("user_code.py", "r", encoding="utf-8") as f:
        user_source = f.read()

    exec(user_source, global_ns)

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

const VALIDATE_DRIVER = `
import sys
import os
import builtins
import pandas as pd
import warnings

warnings.simplefilter("ignore")
sys.path.append(os.getcwd())

if os.path.exists("data.csv"):
    try:
        loaded_df = pd.read_csv("data.csv")
        loaded_df.columns = loaded_df.columns.str.lower().str.strip()
        builtins.data = loaded_df
        builtins.df = loaded_df
    except Exception:
        pass

try:
    try:
        from _env import get_llm
        import builtins
        builtins.get_llm = get_llm
    except Exception:
        pass

    import validator
    import user_code

    result = validator.validate(user_code)
    if result is not None:
        print(result)
except Exception as e:
    print(f"Validation Wrapper Error: {e}")
    import traceback
    traceback.print_exc()
`;

@Injectable()
export class DockerExecutorService implements OnModuleInit {
  private docker: Docker | null = null;
  private available = false;
  private limit: ReturnType<typeof pLimit>;
  private runsDir: string;
  private questionsDir: string;
  private memoryLimit: string;
  private timeout: number;

  constructor(private readonly config: ConfigService) {
    this.limit = pLimit(5);
    this.runsDir = path.resolve(
      this.config.get<string>('questionsDir')!,
      '..',
      'backend',
      'runs',
    );
    this.questionsDir = this.config.get<string>('questionsDir')!;
    this.memoryLimit = this.config.get<string>('docker.memoryLimit')!;
    this.timeout = this.config.get<number>('docker.timeout')!;
  }

  async onModuleInit() {
    try {
      this.docker = new Docker();
      await this.docker.ping();
      this.available = true;
    } catch (e) {
      console.warn(`Docker not available: ${e}`);
      this.docker = null;
      this.available = false;
    }

    fs.mkdirSync(this.runsDir, { recursive: true });
  }

  isAvailable(): boolean {
    return this.available;
  }

  async runCode(
    code: string,
    questionFolderPath: string,
    imageName: string,
    envVars: Record<string, string>,
    networkEnabled: boolean,
  ): Promise<ExecutionResult> {
    return this.limit(() =>
      this.executeContainer(
        code,
        questionFolderPath,
        imageName,
        envVars,
        false,
        networkEnabled,
      ),
    );
  }

  /**
   * Runs a self-contained Python script directly in a Docker container.
   * No driver scripts, no question folder — the code must be fully prepared
   * (e.g. via buildRunScript in ExecuteService).
   */
  async runScript(code: string, imageName: string): Promise<ExecutionResult> {
    if (!this.docker) {
      return {
        stdout: '',
        stderr: 'Docker is not available. Code execution disabled.',
        artifacts: [],
        status: 'error',
      };
    }

    const runId = uuidv4();
    const workDir = path.join(this.runsDir, runId);
    fs.mkdirSync(workDir, { recursive: true });

    try {
      fs.writeFileSync(path.join(workDir, 'script.py'), code, 'utf-8');

      const memBytes = this.parseMemoryLimit(this.memoryLimit);

      const container = await this.docker.createContainer({
        Image: imageName,
        Cmd: ['python', '-W', 'ignore', 'script.py'],
        Env: ['PYTHONWARNINGS=ignore', 'PYTHONIOENCODING=utf-8'],
        HostConfig: {
          Binds: [`${workDir}:/workspace:rw`],
          Memory: memBytes,
          MemorySwap: memBytes,
          CpuPeriod: 100000,
          CpuQuota: 50000,
          NetworkMode: 'none',
        },
        WorkingDir: '/workspace',
        User: 'runner',
      });

      await container.start();

      let exitCode = 1;
      try {
        const waitResult = await Promise.race([
          container.wait(),
          new Promise<never>((_, reject) =>
            setTimeout(() => reject(new Error('timeout')), this.timeout * 1000),
          ),
        ]);
        exitCode = (waitResult as any).StatusCode ?? 1;
      } catch {
        try { await container.kill(); } catch {}
        return {
          stdout: '',
          stderr: `Execution timed out after ${this.timeout} seconds`,
          artifacts: [],
          status: 'error',
          run_id: runId,
        };
      }

      const stdoutBuf = await container.logs({ stdout: true, stderr: false });
      const stderrBuf = await container.logs({ stdout: false, stderr: true });

      let stdout = this.stripDockerHeaders(stdoutBuf);
      let stderr = this.stripDockerHeaders(stderrBuf);

      try { await container.remove({ force: true }); } catch {}

      const MAX = 50000;
      if (stdout.length > MAX) stdout = stdout.substring(0, MAX) + '\n... [Output truncated]';
      if (stderr.length > MAX) stderr = stderr.substring(0, MAX) + '\n... [Error truncated]';

      return { stdout, stderr, artifacts: [], status: exitCode === 0 ? 'success' : 'error', run_id: runId };
    } catch (e: any) {
      if (e.statusCode === 404) {
        return {
          stdout: '',
          stderr: `Docker image not found: ${imageName}. Build it with: docker build -t ${imageName} -f backend/Dockerfile.python-executor backend/`,
          artifacts: [],
          status: 'error',
          run_id: runId,
        };
      }
      return {
        stdout: '',
        stderr: `Docker execution error: ${e.message}`,
        artifacts: [],
        status: 'error',
        run_id: runId,
      };
    }
  }

  async validateCode(
    code: string,
    questionFolderPath: string,
    imageName: string,
    envVars: Record<string, string>,
    networkEnabled: boolean,
  ): Promise<ExecutionResult> {
    return this.limit(() =>
      this.executeContainer(
        code,
        questionFolderPath,
        imageName,
        envVars,
        true,
        networkEnabled,
      ),
    );
  }

  private async executeContainer(
    code: string,
    questionFolderPath: string,
    imageName: string,
    envVars: Record<string, string>,
    isValidation: boolean,
    networkEnabled: boolean,
  ): Promise<ExecutionResult> {
    if (!this.docker) {
      return {
        stdout: '',
        stderr: 'Docker is not available. Code execution disabled for security.',
        artifacts: [],
        status: 'error',
      };
    }

    const runId = uuidv4();
    const workDir = path.join(this.runsDir, runId);
    fs.mkdirSync(workDir, { recursive: true });

    try {
      // Write user code
      fs.writeFileSync(path.join(workDir, 'user_code.py'), code, 'utf-8');

      // Write driver script
      const driverFile = isValidation ? 'validate_driver.py' : 'main.py';
      const driverCode = isValidation ? VALIDATE_DRIVER : RUN_DRIVER;
      fs.writeFileSync(path.join(workDir, driverFile), driverCode, 'utf-8');

      // Copy validator.py for validation
      if (isValidation) {
        const valPath = path.join(questionFolderPath, 'validator.py');
        if (fs.existsSync(valPath)) {
          fs.copyFileSync(valPath, path.join(workDir, 'validator.py'));
        } else {
          return {
            stdout: '',
            stderr: 'Validator script not found in question folder',
            artifacts: [],
            status: 'error',
            run_id: runId,
          };
        }
      }

      // Copy data files from question folder
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

      // Copy shared utils
      const utilsDir = path.join(this.questionsDir, 'utils');
      if (fs.existsSync(utilsDir)) {
        for (const f of fs.readdirSync(utilsDir)) {
          if (f.endsWith('.py')) {
            fs.copyFileSync(
              path.join(utilsDir, f),
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

      // Container env
      const containerEnv: string[] = [
        'PYTHONWARNINGS=ignore',
        'PYTHONIOENCODING=utf-8',
        ...Object.entries(envVars).map(([k, v]) => `${k}=${v}`),
      ];

      // Parse memory limit to bytes
      const memBytes = this.parseMemoryLimit(this.memoryLimit);

      // Create and run container
      const container = await this.docker.createContainer({
        Image: imageName,
        Cmd: isValidation
          ? ['python', '-W', 'ignore', 'validate_driver.py']
          : ['python', '-W', 'ignore', 'main.py'],
        Env: containerEnv,
        HostConfig: {
          Binds: [`${workDir}:/workspace:rw`],
          Memory: memBytes,
          MemorySwap: memBytes,
          CpuPeriod: 100000,
          CpuQuota: 50000,
          NetworkMode: networkEnabled ? 'bridge' : 'none',
        },
        WorkingDir: '/workspace',
        User: 'runner',
      });

      await container.start();

      // Wait with timeout
      let exitCode = 1;
      try {
        const waitResult = await Promise.race([
          container.wait(),
          new Promise<never>((_, reject) =>
            setTimeout(
              () => reject(new Error('timeout')),
              this.timeout * 1000,
            ),
          ),
        ]);
        exitCode = (waitResult as any).StatusCode ?? 1;
      } catch {
        try {
          await container.kill();
        } catch {}
        return {
          stdout: '',
          stderr: `Execution timed out after ${this.timeout} seconds`,
          artifacts: [],
          status: 'error',
          run_id: runId,
        };
      }

      // Get logs
      const stdoutBuf = await container.logs({
        stdout: true,
        stderr: false,
      });
      const stderrBuf = await container.logs({
        stdout: false,
        stderr: true,
      });

      let stdout = this.stripDockerHeaders(stdoutBuf);
      let stderr = this.stripDockerHeaders(stderrBuf);

      // Cleanup container
      try {
        await container.remove({ force: true });
      } catch {}

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

      // Truncate output (50KB)
      const MAX = 50000;
      if (stdout.length > MAX)
        stdout =
          stdout.substring(0, MAX) +
          '\n... [Output truncated due to excessive length]';
      if (stderr.length > MAX)
        stderr =
          stderr.substring(0, MAX) +
          '\n... [Error output truncated due to excessive length]';

      return {
        stdout,
        stderr,
        artifacts,
        status: exitCode === 0 ? 'success' : 'error',
        run_id: runId,
      };
    } catch (e: any) {
      if (e.statusCode === 404) {
        return {
          stdout: '',
          stderr: `Docker image not found: ${imageName}. Build with: docker build -t ${imageName} -f docker/Dockerfile.python .`,
          artifacts: [],
          status: 'error',
          run_id: runId,
        };
      }
      return {
        stdout: '',
        stderr: `Docker execution error: ${e.message}`,
        artifacts: [],
        status: 'error',
        run_id: runId,
      };
    }
  }

  private parseMemoryLimit(limit: string): number {
    const match = limit.match(/^(\d+)([mgk]?)$/i);
    if (!match) return 128 * 1024 * 1024;
    const num = parseInt(match[1]);
    const unit = (match[2] || 'm').toLowerCase();
    if (unit === 'g') return num * 1024 * 1024 * 1024;
    if (unit === 'k') return num * 1024;
    return num * 1024 * 1024;
  }

  private stripDockerHeaders(buf: any): string {
    // Docker multiplexed stream has 8-byte headers per frame
    if (Buffer.isBuffer(buf)) {
      return buf.toString('utf-8');
    }
    if (typeof buf === 'string') return buf;
    return String(buf);
  }

  getRunsDir(): string {
    return this.runsDir;
  }
}
