
import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { HttpService } from '@nestjs/axios';
import { lastValueFrom } from 'rxjs';
import { ExecutionResult } from './docker-executor.service.js';

@Injectable()
export class Judge0Service {
    private readonly logger = new Logger(Judge0Service.name);
    private apiUrl: string;
    private apiKey: string | undefined;
    private cachedPythonLanguageId: number | null = null;
    private configuredPythonLanguageId: number | null = null;

    constructor(
        private readonly configService: ConfigService,
        private readonly httpService: HttpService,
    ) {
        this.apiUrl = this.configService.get<string>('judge0.apiUrl', 'http://localhost:2358');
        this.apiKey = this.configService.get<string>('judge0.apiKey'); // Optional if self-hosted
        const configured = this.configService.get<string>('judge0.pythonLanguageId');
        const parsed = configured ? Number(configured) : NaN;
        if (Number.isInteger(parsed) && parsed > 0) {
            this.configuredPythonLanguageId = parsed;
            this.logger.log(`Using configured Judge0 Python language_id=${parsed}`);
        }
    }

    async runCode(
        code: string,
        languageId?: number,
        stdin?: string,
    ): Promise<ExecutionResult> {
        try {
            const resolvedLanguageId = languageId ?? await this.getPythonLanguageId();

            const payload = {
                source_code: Buffer.from(code).toString('base64'),
                language_id: resolvedLanguageId,
                stdin: stdin ? Buffer.from(stdin).toString('base64') : undefined,
            };

            const headers: Record<string, string> = { 'Content-Type': 'application/json' };
            if (this.apiKey) {
                headers['X-Auth-Token'] = this.apiKey;
            }

            // Step 1: Submit asynchronously (no wait=true — avoids ECONNRESET on long-running submissions)
            this.logger.log(`Submitting code to Judge0 at ${this.apiUrl}/submissions`);
            const submitResponse = await lastValueFrom(
                this.httpService.post(
                    `${this.apiUrl}/submissions?base64_encoded=true`,
                    payload,
                    { headers },
                )
            );

            const token: string = submitResponse.data?.token;
            if (!token) {
                throw new Error('Judge0 did not return a submission token');
            }

            // Step 2: Poll until status.id >= 3 (finished)
            const POLL_INTERVAL_MS = 500;
            const MAX_WAIT_MS = 30_000;
            const deadline = Date.now() + MAX_WAIT_MS;

            while (Date.now() < deadline) {
                await new Promise(resolve => setTimeout(resolve, POLL_INTERVAL_MS));

                const pollResponse = await lastValueFrom(
                    this.httpService.get(
                        `${this.apiUrl}/submissions/${token}?base64_encoded=true`,
                        { headers },
                    )
                );

                const result = pollResponse.data;
                const statusId: number = result.status?.id ?? 0;

                // 1 = In Queue, 2 = Processing — keep waiting
                if (statusId <= 2) continue;

                // Finished — decode and return
                const stdout = result.stdout ? Buffer.from(result.stdout, 'base64').toString('utf-8') : '';
                const stderr = result.stderr ? Buffer.from(result.stderr, 'base64').toString('utf-8') : '';
                const compileOutput = result.compile_output ? Buffer.from(result.compile_output, 'base64').toString('utf-8') : '';
                const message = result.message ? Buffer.from(result.message, 'base64').toString('utf-8') : '';

                const finalStderr = [stderr, compileOutput, message].filter(Boolean).join('\n');

                // Status ID 3 = Accepted (success), anything else = error
                const status = statusId === 3 ? 'success' : 'error';

                return { stdout, stderr: finalStderr, artifacts: [], status, run_id: token };
            }

            return {
                stdout: '',
                stderr: 'Execution timed out waiting for Judge0 result (30s)',
                artifacts: [],
                status: 'error',
            };

        } catch (error: any) {
            this.logger.error(`Judge0 execution failed: ${error.message}`, error.stack);
            return {
                stdout: '',
                stderr: `Execution Environment Error: ${error.message}`,
                artifacts: [],
                status: 'error',
            };
        }
    }

    private async getPythonLanguageId(): Promise<number> {
        if (this.configuredPythonLanguageId) return this.configuredPythonLanguageId;
        if (this.cachedPythonLanguageId) return this.cachedPythonLanguageId;

        try {
            const headers: Record<string, string> = {};
            if (this.apiKey) {
                headers['X-Auth-Token'] = this.apiKey;
            }

            const response = await lastValueFrom(
                this.httpService.get(`${this.apiUrl}/languages`, { headers }),
            );

            const languages = Array.isArray(response.data) ? response.data : [];
            const python3 = languages.find(
                (l: any) =>
                    typeof l?.name === 'string' &&
                    l.name.toLowerCase().includes('python') &&
                    l.name.toLowerCase().includes('(3'),
            );

            if (python3?.id) {
                this.cachedPythonLanguageId = Number(python3.id);
                this.logger.log(`Resolved Judge0 Python language_id=${this.cachedPythonLanguageId}`);
                return this.cachedPythonLanguageId;
            }
        } catch (error: any) {
            this.logger.warn(`Failed to auto-detect Judge0 Python language: ${error.message}`);
        }

        // Fallback for older Judge0 CE builds.
        return 71;
    }

    isAvailable(): boolean {
        return !!this.apiUrl;
    }
}
