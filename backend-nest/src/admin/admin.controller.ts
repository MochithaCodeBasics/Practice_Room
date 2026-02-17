import {
  Controller,
  Post,
  Put,
  Delete,
  Param,
  Body,
  UseGuards,
  UseInterceptors,
  UploadedFiles,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { FileFieldsInterceptor } from '@nestjs/platform-express';
import { AdminService } from './admin.service.js';
import { JwtAuthGuard } from '../common/guards/jwt-auth.guard.js';
import { AdminGuard } from '../common/guards/admin.guard.js';

@Controller('api/v1/admin')
@UseGuards(JwtAuthGuard, AdminGuard)
export class AdminController {
  constructor(private readonly adminService: AdminService) {}

  @Post('questions')
  @HttpCode(HttpStatus.CREATED)
  @UseInterceptors(
    FileFieldsInterceptor([
      { name: 'question_py', maxCount: 1 },
      { name: 'validator_py', maxCount: 1 },
      { name: 'data_files', maxCount: 10 },
    ]),
  )
  async createQuestion(
    @Body()
    body: {
      title: string;
      difficulty: string;
      module_id: string;
      tags?: string;
      topic?: string;
      question_text?: string;
      validator_text?: string;
      data_file_content?: string;
      data_file_name?: string;
    },
    @UploadedFiles()
    files: {
      question_py?: Express.Multer.File[];
      validator_py?: Express.Multer.File[];
      data_files?: Express.Multer.File[];
    },
  ) {
    return this.adminService.createQuestion({
      title: body.title,
      difficulty: body.difficulty,
      module_id: body.module_id,
      tags: body.tags,
      topic: body.topic,
      questionPyFile: files?.question_py?.[0],
      questionPyContent: body.question_text,
      validatorPyFile: files?.validator_py?.[0],
      validatorPyContent: body.validator_text,
      dataFiles: files?.data_files,
      dataFileContent: body.data_file_content,
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
    FileFieldsInterceptor([
      { name: 'question_py', maxCount: 1 },
      { name: 'validator_py', maxCount: 1 },
      { name: 'data_files', maxCount: 10 },
    ]),
  )
  async updateQuestion(
    @Param('questionId') questionId: string,
    @Body()
    body: {
      title?: string;
      difficulty?: string;
      topic?: string;
      tags?: string;
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
}
