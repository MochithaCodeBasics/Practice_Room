import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Param,
  Body,
  Query,
  UseGuards,
  UseInterceptors,
  UploadedFiles,
  HttpCode,
  HttpStatus,
  HttpException,
} from '@nestjs/common';
import { FileFieldsInterceptor } from '@nestjs/platform-express';
import * as multer from 'multer';
import { AdminService } from './admin.service.js';
import { CodebasicsAuthGuard } from '../common/guards/codebasics-auth.guard.js';
import { AdminGuard } from '../common/guards/admin.guard.js';
import { CreateAdminQuestionDto } from './dto/create-admin-question.dto.js';

@Controller('api/v1/admin')
@UseGuards(CodebasicsAuthGuard, AdminGuard)
export class AdminController {
  constructor(private readonly adminService: AdminService) {}

  @Get('question-templates')
  async getQuestionTemplates(@Query('type') type?: string) {
    if (!type) {
      return this.adminService.getAllTemplates();
    }

    if (type !== 'question' && type !== 'validator') {
      throw new HttpException(
        'Invalid type. Use "question" or "validator".',
        HttpStatus.BAD_REQUEST,
      );
    }

    return this.adminService.getTemplate(type);
  }

  @Get('questions')
  async getQuestions() {
    return this.adminService.getQuestions();
  }

  @Post('questions')
  @HttpCode(HttpStatus.CREATED)
  @UseInterceptors(
    FileFieldsInterceptor(
      [
        { name: 'question_py', maxCount: 1 },
        { name: 'validator_py', maxCount: 1 },
        { name: 'data_files', maxCount: 10 },
      ],
      { storage: multer.memoryStorage() },
    ),
  )
  async createQuestion(
    @Body() body: CreateAdminQuestionDto,
    @UploadedFiles()
    files: {
      question_py?: Express.Multer.File[];
      validator_py?: Express.Multer.File[];
      data_files?: Express.Multer.File[];
    },
  ) {
    const questionPyFile = files?.question_py?.[0];
    const validatorPyFile = files?.validator_py?.[0];

    if (!body.title?.trim()) {
      throw new HttpException('title is required', HttpStatus.BAD_REQUEST);
    }
    if (!body.module_id?.trim()) {
      throw new HttpException('module_id is required', HttpStatus.BAD_REQUEST);
    }
    if (!body.difficulty?.trim()) {
      throw new HttpException('difficulty is required', HttpStatus.BAD_REQUEST);
    }
    if (!questionPyFile) {
      throw new HttpException(
        'question_py file is required',
        HttpStatus.BAD_REQUEST,
      );
    }
    if (!validatorPyFile) {
      throw new HttpException(
        'validator_py file is required',
        HttpStatus.BAD_REQUEST,
      );
    }

    return this.adminService.createQuestion({
      title: body.title,
      difficulty: body.difficulty,
      module_id: body.module_id,
      tags: body.tags,
      topic: body.topic,
      questionPyFile,
      questionPyContent: questionPyFile.buffer.toString('utf-8'),
      validatorPyFile,
      validatorPyContent: validatorPyFile.buffer.toString('utf-8'),
      dataFiles: files?.data_files,
      dataFileContent: body.sample_data ?? body.data_file_content,
      dataFileName: body.data_file_name,
    });
  }

  @Delete('questions/:questionId')
  @HttpCode(HttpStatus.NO_CONTENT)
  async deleteQuestion(@Param('questionId') questionId: string) {
    await this.adminService.deleteQuestion(questionId);
  }

  @Put('questions/:questionId')
  @UseInterceptors(
    FileFieldsInterceptor(
      [
        { name: 'question_py', maxCount: 1 },
        { name: 'validator_py', maxCount: 1 },
        { name: 'data_files', maxCount: 10 },
      ],
      { storage: multer.memoryStorage() },
    ),
  )
  async updateQuestion(
    @Param('questionId') questionId: string,
    @Body()
    body: {
      title?: string;
      difficulty?: string;
      topic?: string;
      tags?: string;
      is_active?: string;
    },
    @UploadedFiles()
    files: {
      question_py?: Express.Multer.File[];
      validator_py?: Express.Multer.File[];
      data_files?: Express.Multer.File[];
    },
  ) {
    return this.adminService.updateQuestion(questionId, {
      title: body.title,
      difficulty: body.difficulty,
      topic: body.topic,
      tags: body.tags,
      is_active: body.is_active !== undefined ? body.is_active === 'true' : undefined,
      questionPyFile: files?.question_py?.[0],
      validatorPyFile: files?.validator_py?.[0],
      dataFiles: files?.data_files,
    });
  }

  @Post('questions/:questionId/verify')
  async verifyQuestion(
    @Param('questionId') questionId: string,
    @Body() body: { verified: boolean },
  ) {
    return this.adminService.verifyQuestion(questionId, body.verified);
  }

  @Post('questions/:questionId/activate')
  async setQuestionActive(
    @Param('questionId') questionId: string,
    @Body() body: { active: boolean },
  ) {
    return this.adminService.setQuestionActive(questionId, body.active);
  }
}
