import {
  Injectable,
  CanActivate,
  ExecutionContext,
} from '@nestjs/common';

/**
 * Temporary stub — always allows access.
 * TODO: Restore full JWT + revoked-token + user DB validation
 *       once auth tables (users, revoked_tokens) are migrated.
 */
@Injectable()
export class JwtAuthGuard implements CanActivate {
  canActivate(_context: ExecutionContext): boolean {
    return true;
  }
}
