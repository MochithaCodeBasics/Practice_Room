import {
  Controller,
  Logger,
  Post,
  Get,
  Body,
  Param,
  Res,
  UseGuards,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { Type } from 'class-transformer';
import { IsInt, IsString, Min } from 'class-validator';
import type { Response } from 'express';
import * as fs from 'fs';
import * as path from 'path';
import { ExecuteService } from './execute.service.js';
import { DockerExecutorService } from './docker-executor.service.js';
import { ProgressService } from '../progress/progress.service.js';
import { PrismaService } from '../prisma/prisma.service.js';
import { CodebasicsAuthGuard } from '../common/guards/codebasics-auth.guard.js';
import { CurrentUser } from '../common/decorators/current-user.decorator.js';

class ExecutionRequestDto {
  @IsString()
  code: string;

  @Type(() => Number)
  @IsInt()
  @Min(1)
  question_id: number;

  @Type(() => Number)
  @IsInt()
  @Min(1)
  module_id: number;
}

@Controller('api/execute')
export class ExecuteController {
  private readonly logger = new Logger(ExecuteController.name);

  constructor(
    private readonly executeService: ExecuteService,
    private readonly dockerExecutor: DockerExecutorService,
    private readonly progressService: ProgressService,
    private readonly prisma: PrismaService,
  ) {}

  @Post('run')
  @UseGuards(CodebasicsAuthGuard)
  async runCode(
    @Body() dto: ExecutionRequestDto,
    @CurrentUser() user: any,
  ) {
    const questionId = String(dto.question_id);
    const moduleId = String(dto.module_id);

    return this.executeService.runCode(
      dto.code,
      questionId,
      moduleId,
      user,
    );
  }

  @Post('validate')
  @UseGuards(CodebasicsAuthGuard)
  async validateCode(
    @Body() dto: ExecutionRequestDto,
    @CurrentUser() user: any,
  ) {
    const questionId = String(dto.question_id);
    const moduleId = String(dto.module_id);

    const result = await this.executeService.validateCode(
      dto.code,
      questionId,
      moduleId,
      user,
    );

    // Track progress — user is guaranteed authenticated by CodebasicsAuthGuard
    const isPass =
      result.status === 'success' &&
      result.stdout &&
      (result.stdout.toLowerCase().includes('[pass]') ||
        result.stdout.toLowerCase().includes('correct!') ||
        result.stdout.includes('\u2705'));

    if (isPass) {
      await this.progressService.markCompleted(user.id, questionId, dto.code);
    } else {
      await this.progressService.markAttempted(user.id, questionId, dto.code);
    }

    // Record submission — fire-and-forget so DB errors never block the response
    this.prisma.userSubmission.create({
      data: {
        user_id: user.id,
        question_id: questionId,
        submitted_code: dto.code,
        stdout: result.stdout ?? null,
        stderr: result.stderr ?? null,
        status: isPass ? 'pass' : 'fail',
      },
    }).catch((err) => this.logger.error('Failed to record submission', err));

    return result;
  }

  @Get('runs/:runId/:filename')
  async getArtifact(
    @Param('runId') runId: string,
    @Param('filename') filename: string,
    @Res() res: Response,
  ) {
    // Validate UUID format
    const uuidRegex =
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(runId)) {
      throw new HttpException('Invalid run ID', HttpStatus.BAD_REQUEST);
    }

    // Security: prevent path traversal
    if (
      filename.includes('..') ||
      filename.includes('/') ||
      filename.includes('\\')
    ) {
      throw new HttpException('Invalid filename', HttpStatus.BAD_REQUEST);
    }

    // Only allow PNG files
    if (!filename.endsWith('.png')) {
      throw new HttpException(
        'Only PNG files are allowed',
        HttpStatus.BAD_REQUEST,
      );
    }

    const filePath = path.join(
      this.dockerExecutor.getRunsDir(),
      runId,
      filename,
    );

    if (!fs.existsSync(filePath)) {
      throw new HttpException('File not found', HttpStatus.NOT_FOUND);
    }

    res.sendFile(filePath);
  }
}
