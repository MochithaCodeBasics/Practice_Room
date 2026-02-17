import {
  Injectable,
  CanActivate,
  ExecutionContext,
  Logger,
} from '@nestjs/common';

interface CachedUser {
  data: Record<string, unknown>;
  expiresAt: number;
}

const TOKEN_CACHE = new Map<string, CachedUser>();
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

@Injectable()
export class CodebasicsOptionalAuthGuard implements CanActivate {
  private readonly logger = new Logger(CodebasicsOptionalAuthGuard.name);

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
        request.user = null;
        return true;
      }

      const userData = await response.json();

      TOKEN_CACHE.set(token, {
        data: userData,
        expiresAt: Date.now() + CACHE_TTL_MS,
      });

      request.user = userData;
    } catch (error) {
      this.logger.warn('Failed to validate token with Codebasics API', error);
      request.user = null;
    }

    return true;
  }
}
