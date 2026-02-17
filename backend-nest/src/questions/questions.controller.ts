import {
  Controller,
  Get,
  Param,
  Query,
  UseGuards,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { QuestionsService } from './questions.service.js';
import { OptionalAuthGuard } from '../common/guards/optional-auth.guard.js';
import { CurrentUser } from '../common/decorators/current-user.decorator.js';

@Controller('api/questions')
export class QuestionsController {
  constructor(private readonly questionsService: QuestionsService) {}

  @Get()
  @UseGuards(OptionalAuthGuard)
  async findAll(
    @CurrentUser() user: any,
    @Query('difficulty') difficulty?: string,
    @Query('status') status?: string,
  ) {
    return this.questionsService.getAllQuestions(
      user?.username,
      difficulty,
      status,
      user?.role,
    );
  }

  @Get(':questionId')
  @UseGuards(OptionalAuthGuard)
  async findOne(
    @Param('questionId') questionId: string,
    @CurrentUser() user: any,
  ) {
    const question = await this.questionsService.getQuestion(
      questionId,
      user?.username,
      user?.role,
    );

    if (!question) {
      throw new HttpException('Question not found', HttpStatus.NOT_FOUND);
    }

    return question;
  }
}
