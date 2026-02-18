
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

            // Prepare submission payload
            // base64 encoding is recommended for source_code and stdin/stdout
            const payload = {
                source_code: Buffer.from(code).toString('base64'),
                language_id: resolvedLanguageId,
                stdin: stdin ? Buffer.from(stdin).toString('base64') : undefined,
                wait: true, // Wait for the result
            };

            const headers: any = {
                'Content-Type': 'application/json',
            };

            if (this.apiKey) {
                headers['X-Auth-Token'] = this.apiKey;
            }

            this.logger.log(`Submitting code to Judge0 at ${this.apiUrl}/submissions?base64_encoded=true&wait=true`);

            const response = await lastValueFrom(
                this.httpService.post(
                    `${this.apiUrl}/submissions?base64_encoded=true&wait=true`,
                    payload,
                    { headers }
                )
            );

            const result = response.data;

            // Decode output
            const stdout = result.stdout ? Buffer.from(result.stdout, 'base64').toString('utf-8') : '';
            const stderr = result.stderr ? Buffer.from(result.stderr, 'base64').toString('utf-8') : '';
            const compileOutput = result.compile_output ? Buffer.from(result.compile_output, 'base64').toString('utf-8') : '';
            const message = result.message ? Buffer.from(result.message, 'base64').toString('utf-8') : '';

            const finalStderr = [stderr, compileOutput, message].filter(Boolean).join('\n');

            // Status ID 3 means "Accepted"
            const status = result.status?.id === 3 ? 'success' : 'error';

            // If there's a runtime error (status.id != 3), we treat it as an error
            // Note: stdout might still have some output even on error

            return {
                stdout,
                stderr: finalStderr,
                artifacts: [], // Judge0 doesn't support file artifacts in the basic version easily
                status,
                run_id: result.token,
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
