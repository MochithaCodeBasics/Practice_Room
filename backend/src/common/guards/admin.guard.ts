import {
  Injectable,
  CanActivate,
  ExecutionContext,
  ForbiddenException,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class AdminGuard implements CanActivate {
  constructor(private readonly configService: ConfigService) {}

  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const user = request.user;

    if (!user) {
      throw new ForbiddenException('Access denied');
    }

    const adminEmails: string[] =
      this.configService.get<string[]>('admin.emails') || [];
    const userEmail = (user.email as string)?.toLowerCase();
    const roleCandidates = [
      user.role,
      user.role_name,
      user.roleName,
    ]
      .map((r) => (typeof r === 'string' ? r.toLowerCase() : ''))
      .filter(Boolean);
    const isAdminRole = roleCandidates.includes('admin');

    if (isAdminRole) {
      return true;
    }

    if (userEmail && adminEmails.includes(userEmail)) {
      return true;
    }

    throw new ForbiddenException('Admin access required');
  }
}
