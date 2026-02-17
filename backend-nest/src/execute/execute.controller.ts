import {
  Controller,
  Post,
  Get,
  Body,
  Param,
  Res,
  UseGuards,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import type { Response } from 'express';
import * as fs from 'fs';
import * as path from 'path';
import { ExecuteService } from './execute.service.js';
import { DockerExecutorService } from './docker-executor.service.js';
import { ProgressService } from '../progress/progress.service.js';
import { PrismaService } from '../prisma/prisma.service.js';
import { OptionalAuthGuard } from '../common/guards/optional-auth.guard.js';
import { CurrentUser } from '../common/decorators/current-user.decorator.js';

class ExecutionRequestDto {
  code: string;
  question_id: string;
  module_id: string;
}

@Controller('api/execute')
export class ExecuteController {
  constructor(
    private readonly executeService: ExecuteService,
    private readonly dockerExecutor: DockerExecutorService,
    private readonly progressService: ProgressService,
    private readonly prisma: PrismaService,
  ) {}

  @Post('run')
  @UseGuards(OptionalAuthGuard)
  async runCode(
    @Body() dto: ExecutionRequestDto,
    @CurrentUser() user: any,
  ) {
    return this.executeService.runCode(
      dto.code,
      dto.question_id,
      dto.module_id,
      user,
    );
  }

  @Post('validate')
  @UseGuards(OptionalAuthGuard)
  async validateCode(
    @Body() dto: ExecutionRequestDto,
    @CurrentUser() user: any,
  ) {
    const result = await this.executeService.validateCode(
      dto.code,
      dto.question_id,
      dto.module_id,
      user,
    );

    // Track progress if user is authenticated
    if (user?.username) {
      const isPass =
        result.status === 'success' &&
        result.stdout &&
        (result.stdout.toLowerCase().includes('[pass]') ||
          result.stdout.toLowerCase().includes('correct!') ||
          result.stdout.includes('\u2705'));

      if (isPass) {
        await this.progressService.markCompleted(
          user.username,
          dto.question_id,
          dto.code,
        );
        // Fetch updated streak
        const updatedUser = await this.prisma.user.findUnique({
          where: { username: user.username },
        });
        if (updatedUser) {
          result.current_streak = updatedUser.current_streak;
        }
      } else {
        await this.progressService.markAttempted(
          user.username,
          dto.question_id,
          dto.code,
        );
        result.current_streak = user.current_streak;
      }
    }

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
