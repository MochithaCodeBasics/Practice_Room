import { Controller, Get } from '@nestjs/common';

@Controller()
export class AppController {
  @Get()
  root() {
    return { message: 'Welcome to the Practice Room API' };
  }

  @Get('health')
  healthCheck() {
    return { status: 'ok' };
  }
}
