import { Injectable } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { PrismaService } from '../prisma/prisma.service.js';

@Injectable()
export class AuthService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly jwtService: JwtService,
  ) {}

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
}
