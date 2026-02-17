import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import type { Response } from 'express';

/**
 * Maps NestJS error responses to FastAPI-compatible format.
 * FastAPI returns { detail: string }, NestJS returns { statusCode, message, error }.
 * The frontend checks for `response.data.detail`.
 */
@Catch(HttpException)
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: HttpException, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const status = exception.getStatus();
    const exceptionResponse = exception.getResponse();

    let detail: string | object;

    if (typeof exceptionResponse === 'string') {
      detail = exceptionResponse;
    } else if (typeof exceptionResponse === 'object' && exceptionResponse !== null) {
      const resp = exceptionResponse as Record<string, any>;
      // Use 'message' from NestJS response, which may be string or string[]
      detail = resp.message ?? resp.error ?? 'An error occurred';
    } else {
      detail = 'An error occurred';
    }

    response.status(status).json({ detail });
  }
}
