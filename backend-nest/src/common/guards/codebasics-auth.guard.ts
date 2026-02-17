import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
  Logger,
} from '@nestjs/common';

interface CachedUser {
  data: Record<string, unknown>;
  expiresAt: number;
}

const TOKEN_CACHE = new Map<string, CachedUser>();
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

@Injectable()
export class CodebasicsAuthGuard implements CanActivate {
  private readonly logger = new Logger(CodebasicsAuthGuard.name);

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

    // Check cache first
    const cached = TOKEN_CACHE.get(token);
    if (cached && cached.expiresAt > Date.now()) {
      request.user = cached.data;
      return true;
    }

    // Validate token against Codebasics API
    try {
      const response = await fetch('https://codebasics.io/api/user', {
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

      // Cache the validated user
      TOKEN_CACHE.set(token, {
        data: userData,
        expiresAt: Date.now() + CACHE_TTL_MS,
      });

      request.user = userData;
      return true;
    } catch (error) {
      if (error instanceof UnauthorizedException) throw error;
      this.logger.error('Failed to validate token with Codebasics API', error);
      throw new UnauthorizedException('Authentication failed');
    }
  }
}
