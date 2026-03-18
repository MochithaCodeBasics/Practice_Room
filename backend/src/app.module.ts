import { Module, NestModule, MiddlewareConsumer } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { ThrottlerModule, ThrottlerGuard } from '@nestjs/throttler';
import { APP_GUARD } from '@nestjs/core';
import configuration from './config/configuration.js';
import { PrismaModule } from './prisma/prisma.module.js';
import { ModulesModule } from './modules/modules.module.js';
import { QuestionsModule } from './questions/questions.module.js';
import { AdminModule } from './admin/admin.module.js';
import { NoCacheMiddleware } from './common/middleware/no-cache.middleware.js';
import { AppController } from './app.controller.js';

// AuthModule disabled — OAuth with Codebasics replaces local auth
// import { AuthModule } from './auth/auth.module.js';
import { ExecuteModule } from './execute/execute.module.js';
// import { EmailModule } from './email/email.module.js';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true, load: [configuration] }),
    ThrottlerModule.forRoot([{ ttl: 60000, limit: 100 }]),
    PrismaModule,
    ModulesModule,
    QuestionsModule,
    AdminModule,
    ExecuteModule,
  ],
  controllers: [AppController],
  providers: [
    {
      provide: APP_GUARD,
      useClass: ThrottlerGuard,
    },
  ],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer.apply(NoCacheMiddleware).forRoutes('api/*path');
  }
}
