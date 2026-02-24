import { Module } from '@nestjs/common';
import { AdminController } from './admin.controller.js';
import { AdminService } from './admin.service.js';
import { CodebasicsAuthGuard } from '../common/guards/codebasics-auth.guard.js';

@Module({
  controllers: [AdminController],
  providers: [AdminService, CodebasicsAuthGuard],
})
export class AdminModule {}
