import { Module } from '@nestjs/common';
import { ExecuteController } from './execute.controller.js';
import { ExecuteService } from './execute.service.js';
import { DockerExecutorService } from './docker-executor.service.js';
import { Judge0Service } from './judge0.service.js';
import { ProgressModule } from '../progress/progress.module.js';
import { PrismaModule } from '../prisma/prisma.module.js';
import { HttpModule } from '@nestjs/axios';

@Module({
  imports: [ProgressModule, PrismaModule, HttpModule],
  controllers: [ExecuteController],
  providers: [ExecuteService, DockerExecutorService, Judge0Service],
  exports: [ExecuteService],
})
export class ExecuteModule { }
