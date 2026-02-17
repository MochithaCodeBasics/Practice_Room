
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

    constructor(
        private readonly configService: ConfigService,
        private readonly httpService: HttpService,
    ) {
        this.apiUrl = this.configService.get<string>('judge0.apiUrl', 'http://localhost:2358');
        this.apiKey = this.configService.get<string>('judge0.apiKey'); // Optional if self-hosted
    }

    async runCode(
        code: string,
        languageId: number = 71, // 71 is Python (3.8.1) in Judge0
        stdin?: string,
    ): Promise<ExecutionResult> {
        try {
            // Prepare submission payload
            // base64 encoding is recommended for source_code and stdin/stdout
            const payload = {
                source_code: Buffer.from(code).toString('base64'),
                language_id: languageId,
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

    isAvailable(): boolean {
        return !!this.apiUrl;
    }
}
