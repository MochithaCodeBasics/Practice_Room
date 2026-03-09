import { Module } from '@nestjs/common';
import { ModulesController } from './modules.controller.js';
import { ModulesService } from './modules.service.js';
import { ProgressModule } from '../progress/progress.module.js';
import { CodebasicsOptionalAuthGuard } from '../common/guards/codebasics-optional-auth.guard.js';

@Module({
  imports: [ProgressModule],
  controllers: [ModulesController],
  providers: [ModulesService, CodebasicsOptionalAuthGuard],
  exports: [ModulesService],
})
export class ModulesModule {}
