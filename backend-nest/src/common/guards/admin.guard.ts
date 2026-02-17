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

    if (userEmail && adminEmails.includes(userEmail)) {
      return true;
    }

    throw new ForbiddenException('Admin access required');
  }
}
