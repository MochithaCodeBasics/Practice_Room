import { Injectable, ExecutionContext } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { PrismaService } from '../../prisma/prisma.service.js';

@Injectable()
export class OptionalAuthGuard extends AuthGuard('jwt') {
  constructor(private readonly prisma: PrismaService) {
    super();
  }

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const authHeader = request.headers?.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      request.user = null;
      return true;
    }

    try {
      const result = await (super.canActivate(context) as Promise<boolean>);
      if (!result) {
        request.user = null;
        return true;
      }

      const user = request.user;
      if (!user?.jti) {
        request.user = null;
        return true;
      }

      // Check revocation
      const revoked = await this.prisma.revokedToken.findUnique({
        where: { jti: user.jti },
      });
      if (revoked) {
        request.user = null;
        return true;
      }

      // Load full user
      const dbUser = await this.prisma.user.findUnique({
        where: { username: user.username },
      });
      if (!dbUser || dbUser.disabled) {
        request.user = null;
        return true;
      }

      request.user = { ...dbUser, jti: user.jti };
    } catch {
      request.user = null;
    }
    return true;
  }

  handleRequest(err: any, user: any) {
    // Don't throw on missing/invalid token
    return user || null;
  }
}
