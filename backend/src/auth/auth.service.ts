import {
  Injectable,
  UnauthorizedException,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import * as bcrypt from 'bcrypt';
import * as crypto from 'crypto';
import { v4 as uuidv4 } from 'uuid';
import { PrismaService } from '../prisma/prisma.service.js';
import { ProgressService } from '../progress/progress.service.js';

@Injectable()
export class AuthService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly jwtService: JwtService,
    private readonly config: ConfigService,
    private readonly progressService: ProgressService,
  ) {}

  async validateUser(usernameOrEmail: string, password: string) {
    const user = await this.prisma.user.findFirst({
      where: {
        OR: [
          { username: usernameOrEmail },
          { email: usernameOrEmail },
        ],
      },
    });

    if (!user) return null;

    const isValid = await bcrypt.compare(password, user.hashed_password);
    if (!isValid) return null;

    // Refresh streak on login
    await this.progressService.refreshStreak(user.username);

    // Re-fetch to get updated streak
    return this.prisma.user.findUnique({ where: { id: user.id } });
  }

  async login(user: any) {
    const expirationMinutes = this.config.get<number>(
      'jwt.expirationMinutes',
    );
    const payload = {
      sub: user.username,
      role: user.role,
      jti: uuidv4(),
    };

    const accessToken = this.jwtService.sign(payload, {
      expiresIn: (expirationMinutes ?? 1440) * 60,
    });

    return {
      access_token: accessToken,
      token_type: 'bearer',
      role: user.role,
      username: user.username,
      current_streak: user.current_streak,
    };
  }

  async signup(username: string, email: string, password: string) {
    // Check if user already exists
    const existing = await this.prisma.user.findFirst({
      where: { OR: [{ username }, { email }] },
    });

    if (existing) {
      // Anti-enumeration: return a dummy user object
      return {
        id: 0,
        username,
        email,
        role: 'learner',
        disabled: false,
        has_groq_api_key: false,
        has_openai_api_key: false,
        has_anthropic_api_key: false,
        default_llm_provider: 'groq',
        current_streak: 0,
        last_completed_at: null,
        created_at: new Date(),
      };
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = await this.prisma.user.create({
      data: {
        username,
        email,
        hashed_password: hashedPassword,
        role: 'learner',
      },
    });

    return this.sanitizeUser(newUser);
  }

  async getProfile(username: string) {
    const user = await this.prisma.user.findUnique({ where: { username } });
    if (!user) return null;
    return this.sanitizeUser(user);
  }

  async updateSettings(
    userId: number,
    settings: {
      groq_api_key?: string;
      openai_api_key?: string;
      anthropic_api_key?: string;
      default_llm_provider?: string;
    },
  ) {
    const data: any = {};

    if (settings.groq_api_key !== undefined) {
      const stripped = settings.groq_api_key.trim();
      data.groq_api_key = stripped || null;
      data.has_groq_api_key = !!stripped;
    }

    if (settings.openai_api_key !== undefined) {
      const stripped = settings.openai_api_key.trim();
      data.openai_api_key = stripped || null;
      data.has_openai_api_key = !!stripped;
    }

    if (settings.anthropic_api_key !== undefined) {
      const stripped = settings.anthropic_api_key.trim();
      data.anthropic_api_key = stripped || null;
      data.has_anthropic_api_key = !!stripped;
    }

    if (settings.default_llm_provider !== undefined) {
      data.default_llm_provider = settings.default_llm_provider;
    }

    const updated = await this.prisma.user.update({
      where: { id: userId },
      data,
    });

    return {
      message: 'Settings updated successfully',
      has_groq_api_key: updated.has_groq_api_key,
      has_openai_api_key: updated.has_openai_api_key,
      has_anthropic_api_key: updated.has_anthropic_api_key,
      default_llm_provider: updated.default_llm_provider,
    };
  }

  async logout(token: string) {
    try {
      const payload = this.jwtService.verify(token);
      const jti = payload.jti;
      const exp = payload.exp;

      if (jti && exp) {
        const expiresAt = new Date(exp * 1000);
        const existing = await this.prisma.revokedToken.findUnique({
          where: { jti },
        });
        if (!existing) {
          await this.prisma.revokedToken.create({
            data: { jti, expires_at: expiresAt },
          });
        }
      }
    } catch {
      // If token is invalid/expired, nothing to revoke
    }
  }

  async generateResetToken(email: string): Promise<{ username: string; token: string } | null> {
    const user = await this.prisma.user.findUnique({ where: { email } });
    if (!user) return null;

    // Invalidate existing tokens
    await this.prisma.passwordResetToken.updateMany({
      where: { user_id: user.id, used: false },
      data: { used: true },
    });

    // Generate secure token
    const token = crypto.randomBytes(32).toString('base64url');
    const tokenHash = crypto
      .createHash('sha256')
      .update(token)
      .digest('hex');

    await this.prisma.passwordResetToken.create({
      data: {
        user_id: user.id,
        token_hash: tokenHash,
        expires_at: new Date(Date.now() + 60 * 60 * 1000), // 1 hour
      },
    });

    return { username: user.username, token };
  }

  async verifyAndResetPassword(
    token: string,
    newPassword: string,
  ): Promise<boolean> {
    // Password strength validation
    if (newPassword.length < 8) return false;
    if (!/[A-Z]/.test(newPassword)) return false;
    if (!/[a-z]/.test(newPassword)) return false;
    if (!/[0-9]/.test(newPassword)) return false;

    const tokenHash = crypto
      .createHash('sha256')
      .update(token)
      .digest('hex');

    const resetToken = await this.prisma.passwordResetToken.findFirst({
      where: {
        token_hash: tokenHash,
        used: false,
        expires_at: { gt: new Date() },
      },
    });

    if (!resetToken) return false;

    const user = await this.prisma.user.findUnique({
      where: { id: resetToken.user_id },
    });
    if (!user) return false;

    // Prevent admin account takeover via email reset
    if (user.role === 'admin') return false;

    const hashedPassword = await bcrypt.hash(newPassword, 10);

    await this.prisma.$transaction([
      this.prisma.user.update({
        where: { id: user.id },
        data: { hashed_password: hashedPassword },
      }),
      this.prisma.passwordResetToken.update({
        where: { id: resetToken.id },
        data: { used: true },
      }),
    ]);

    return true;
  }

  sanitizeUser(user: any) {
    const {
      hashed_password,
      groq_api_key,
      openai_api_key,
      anthropic_api_key,
      ...safe
    } = user;
    return safe;
  }
}
