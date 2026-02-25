import { Module } from '@nestjs/common';
import { QuestionsController } from './questions.controller.js';
import { QuestionsService } from './questions.service.js';
import { ProgressModule } from '../progress/progress.module.js';
import { PrismaModule } from '../prisma/prisma.module.js';
import { CodebasicsOptionalAuthGuard } from '../common/guards/codebasics-optional-auth.guard.js';

@Module({
  imports: [ProgressModule, PrismaModule],
  controllers: [QuestionsController],
  providers: [QuestionsService, CodebasicsOptionalAuthGuard],
  exports: [QuestionsService],
})
export class QuestionsModule {}
