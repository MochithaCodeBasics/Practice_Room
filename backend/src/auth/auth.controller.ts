import {
  Controller,
  Post,
  Get,
  UseGuards,
  HttpCode,
  HttpStatus,
  Headers,
} from '@nestjs/common';
import { AuthService } from './auth.service.js';
import { CodebasicsAuthGuard } from '../common/guards/codebasics-auth.guard.js';
import { CurrentUser } from '../common/decorators/current-user.decorator.js';

@Controller('api/v1/auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Get('me')
  @UseGuards(CodebasicsAuthGuard)
  getMe(@CurrentUser() user: any) {
    return user;
  }

  @Post('logout')
  @UseGuards(CodebasicsAuthGuard)
  @HttpCode(HttpStatus.OK)
  async logout(@Headers('authorization') authHeader: string) {
    const token = authHeader?.replace('Bearer ', '');
    if (token) {
      await this.authService.logout(token);
    }
    return { message: 'Successfully logged out' };
  }
}
