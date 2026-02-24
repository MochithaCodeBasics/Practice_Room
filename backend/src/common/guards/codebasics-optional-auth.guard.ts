import {
  Injectable,
  CanActivate,
  ExecutionContext,
  Logger,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as bcrypt from 'bcrypt';
import * as crypto from 'crypto';
import { PrismaService } from '../../prisma/prisma.service.js';

interface CachedToken {
  email: string;
  cbId: string;
  expiresAt: number;
}

const TOKEN_CACHE = new Map<string, CachedToken>();
const CACHE_TTL_MS = 48 * 60 * 60 * 1000; // 48 hours

@Injectable()
export class CodebasicsOptionalAuthGuard implements CanActivate {
  private readonly logger = new Logger(CodebasicsOptionalAuthGuard.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly config: ConfigService,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const authHeader = request.headers['authorization'];

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      request.user = null;
      return true;
    }

    const token = authHeader.substring(7);
    if (!token) {
      request.user = null;
      return true;
    }

    let email: string | null = null;
    let cbId = '';

    // Check cache first (stores email + cbId, not raw external user data)
    const cached = TOKEN_CACHE.get(token);
    if (cached && cached.expiresAt > Date.now()) {
      email = cached.email;
      cbId = cached.cbId;
    } else {
      // Validate token against Codebasics API
      try {
        const baseUrl = this.config.get<string>('codebasics.oauthBaseUrl')!;
        const response = await fetch(`${baseUrl}/api/user`, {
          headers: {
            Authorization: `Bearer ${token}`,
            Accept: 'application/json',
          },
        });

        if (!response.ok) {
          TOKEN_CACHE.delete(token);
          request.user = null;
          return true;
        }

        const userData = await response.json();
        email = (userData.email as string) ?? null;
        cbId = String(userData.id ?? '');

        if (email) {
          TOKEN_CACHE.set(token, { email, cbId, expiresAt: Date.now() + CACHE_TTL_MS });
        }
      } catch (error) {
        this.logger.warn('Failed to validate token with Codebasics API', error);
        request.user = null;
        return true;
      }
    }

    if (!email) {
      request.user = null;
      return true;
    }

    // Find or auto-provision a local record for this Codebasics account
    try {
      let localUser = await this.prisma.user.findUnique({ where: { email } });

      if (!localUser) {
        const username = (`cb_${cbId || email.split('@')[0]}`).substring(0, 50);
        const dummyHash = await bcrypt.hash(crypto.randomBytes(32).toString('hex'), 4);

        localUser = await this.prisma.user.upsert({
          where: { email },
          create: { username, email, hashed_password: dummyHash, role: 'learner' },
          update: {},
        });
      }

      request.user = localUser && !localUser.disabled ? localUser : null;
    } catch {
      request.user = null;
    }

    return true;
  }
}
