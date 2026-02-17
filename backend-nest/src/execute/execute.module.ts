import { Module } from '@nestjs/common';
import { ExecuteController } from './execute.controller.js';
import { ExecuteService } from './execute.service.js';
import { DockerExecutorService } from './docker-executor.service.js';
import { ProgressModule } from '../progress/progress.module.js';

@Module({
  imports: [ProgressModule],
  controllers: [ExecuteController],
  providers: [ExecuteService, DockerExecutorService],
})
export class ExecuteModule {}
