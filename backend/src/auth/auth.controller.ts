import {
  Controller,
  Post,
  Get,
  Put,
  Body,
  Req,
  UseGuards,
  HttpCode,
  HttpStatus,
  HttpException,
  Headers,
} from '@nestjs/common';
import { Throttle } from '@nestjs/throttler';
import type { Request } from 'express';
import { AuthService } from './auth.service.js';
import { EmailService } from '../email/email.service.js';
import { JwtAuthGuard } from '../common/guards/jwt-auth.guard.js';
import { CurrentUser } from '../common/decorators/current-user.decorator.js';
import { SignupDto } from './dto/signup.dto.js';
import { UserSettingsDto } from './dto/user-settings.dto.js';
import { ChangePasswordDto } from './dto/change-password.dto.js';

@Controller('api/v1/auth')
export class AuthController {
  constructor(
    private readonly authService: AuthService,
    private readonly emailService: EmailService,
  ) { }

  @Post('login')
  @Throttle({ default: { limit: 5, ttl: 60000 } })
  @HttpCode(HttpStatus.OK)
  async login(@Req() req: Request) {
    // Parse form-urlencoded body (username + password)
    const { username, password } = req.body as any;

    const user = await this.authService.validateUser(username, password);
    if (!user) {
      throw new HttpException(
        'Incorrect username or password',
        HttpStatus.UNAUTHORIZED,
      );
    }

    // Block admin users from learner login
    if (user.role === 'admin') {
      throw new HttpException(
        'Admins must use the admin login portal',
        HttpStatus.FORBIDDEN,
      );
    }

    return this.authService.login(user);
  }

  @Post('admin/login')
  @Throttle({ default: { limit: 5, ttl: 60000 } })
  @HttpCode(HttpStatus.OK)
  async adminLogin(@Req() req: Request) {
    const { username, password } = req.body as any;

    const user = await this.authService.validateUser(username, password);
    if (!user) {
      throw new HttpException(
        'Incorrect username or password',
        HttpStatus.UNAUTHORIZED,
      );
    }

    // Only allow admin users
    if (user.role !== 'admin') {
      throw new HttpException(
        'Access denied. This login is for administrators only.',
        HttpStatus.FORBIDDEN,
      );
    }

    return this.authService.login(user);
  }

  @Get('me')
  @UseGuards(JwtAuthGuard)
  async getMe(@CurrentUser() user: any) {
    return this.authService.sanitizeUser(user);
  }

  @Put('me/settings')
  @UseGuards(JwtAuthGuard)
  async updateSettings(
    @CurrentUser() user: any,
    @Body() dto: UserSettingsDto,
  ) {
    return this.authService.updateSettings(user.id, dto);
  }

  @Put('change-password')
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.OK)
  async changePassword(
    @CurrentUser() user: any,
    @Body() dto: ChangePasswordDto,
  ) {
    return this.authService.changePassword(
      user.id,
      dto.current_password,
      dto.new_password,
    );
  }

  @Post('logout')
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.OK)
  async logout(@Headers('authorization') authHeader: string) {
    const token = authHeader?.replace('Bearer ', '');
    if (token) {
      await this.authService.logout(token);
    }
    return { message: 'Successfully logged out' };
  }

  @Post('signup')
  @HttpCode(HttpStatus.CREATED)
  async signup(@Body() dto: SignupDto) {
    const user = await this.authService.signup(
      dto.username,
      dto.email,
      dto.password,
    );

    // Send welcome email in background (fire-and-forget)
    this.emailService
      .sendWelcomeEmail(dto.email, dto.username)
      .catch(() => { });

    return user;
  }
}
