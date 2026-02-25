import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
  Logger,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../../prisma/prisma.service.js';

interface CachedToken {
  email: string;
  cbId: string;
  expiresAt: number;
}

const TOKEN_CACHE = new Map<string, CachedToken>();
const CACHE_TTL_MS = 48 * 60 * 60 * 1000; // 48 hours

@Injectable()
export class CodebasicsAuthGuard implements CanActivate {
  private readonly logger = new Logger(CodebasicsAuthGuard.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly config: ConfigService,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const authHeader = request.headers['authorization'];

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw new UnauthorizedException('Authentication required');
    }

    const token = authHeader.substring(7);
    if (!token) {
      throw new UnauthorizedException('Authentication required');
    }

    let email: string;
    let cbId: string;

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
          throw new UnauthorizedException('Invalid or expired token');
        }

        const userData = await response.json();
        email = userData.email as string;
        cbId = String(userData.id ?? '');

        if (!email) {
          throw new UnauthorizedException('Could not retrieve email from Codebasics API');
        }

        TOKEN_CACHE.set(token, { email, cbId, expiresAt: Date.now() + CACHE_TTL_MS });
      } catch (error) {
        if (error instanceof UnauthorizedException) throw error;
        this.logger.error('Failed to validate token with Codebasics API', error);
        throw new UnauthorizedException('Authentication failed');
      }
    }

    // Find or auto-provision a local record for this Codebasics account
    let localUser = await this.prisma.user.findUnique({ where: { email } });

    if (!localUser) {
      localUser = await this.prisma.user.upsert({
        where: { email },
        create: { cb_user_id: cbId, email, role: 'learner' },
        update: {},
      });
    }

    request.user = localUser;
    return true;
  }
}
