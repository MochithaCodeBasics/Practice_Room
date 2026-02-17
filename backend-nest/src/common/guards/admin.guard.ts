import {
  Injectable,
  CanActivate,
  ExecutionContext,
} from '@nestjs/common';

/**
 * Temporary stub — always allows access.
 * TODO: Restore admin-role check once auth is fully wired.
 */
@Injectable()
export class AdminGuard implements CanActivate {
  canActivate(_context: ExecutionContext): boolean {
    return true;
  }
}
