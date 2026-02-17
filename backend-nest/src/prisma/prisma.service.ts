import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PrismaMariaDb } from '@prisma/adapter-mariadb';
import { PrismaClient } from '../../generated/prisma/client.js';

@Injectable()
export class PrismaService
  extends PrismaClient
  implements OnModuleInit, OnModuleDestroy {
  constructor(configService: ConfigService) {
    const host = configService.get<string>('database.host')!;
    const port = configService.get<number>('database.port')!;
    const user = configService.get<string>('database.user')!;
    const password = configService.get<string>('database.password')!;
    const dbName = configService.get<string>('database.name')!;
    const connectionString = `mariadb://${user}:${password}@${host}:${port}/${dbName}`;
    const adapter = new PrismaMariaDb(connectionString);
    super({ adapter });
  }

  async onModuleInit() {
    await this.$connect();
  }

  async onModuleDestroy() {
    await this.$disconnect();
  }
}
