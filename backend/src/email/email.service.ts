import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as nodemailer from 'nodemailer';

@Injectable()
export class EmailService {
  private transporter: nodemailer.Transporter | null = null;
  private fromEmail: string;
  private frontendUrl: string;

  constructor(private readonly config: ConfigService) {
    const smtpUser = this.config.get<string>('smtp.user');
    const smtpPassword = this.config.get<string>('smtp.password');
    this.fromEmail =
      this.config.get<string>('smtp.fromEmail') || smtpUser || '';
    this.frontendUrl = this.config.get<string>('frontendUrl')!;

    if (smtpUser && smtpPassword) {
      this.transporter = nodemailer.createTransport({
        host: this.config.get<string>('smtp.host'),
        port: this.config.get<number>('smtp.port'),
        secure: false,
        auth: { user: smtpUser, pass: smtpPassword },
      });
    }
  }

  isConfigured(): boolean {
    return this.transporter !== null;
  }

  async sendPasswordResetEmail(
    toEmail: string,
    username: string,
    resetToken: string,
  ): Promise<boolean> {
    const resetLink = `${this.frontendUrl}/reset-password?token=${resetToken}`;

    if (!this.isConfigured()) {
      console.log(
        `[EMAIL SERVICE] Not configured. Token for ${username}: ${resetToken}`,
      );
      return false;
    }

    const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }
        .button { display: inline-block; background: #405c68; color: #ffffff !important; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .warning { color: #856404; background: #fff3cd; padding: 10px; border-radius: 5px; margin-top: 20px; }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header"><h1>Password Reset</h1></div>
        <div class="content">
          <p>Hello <strong>${username}</strong>,</p>
          <p>We received a request to reset your password for your Practice Room account.</p>
          <p>Click the button below to reset your password:</p>
          <p style="text-align: center;"><a href="${resetLink}" class="button" style="color: #ffffff; text-decoration: none;">Reset Password</a></p>
          <p>Or copy and paste this link into your browser:</p>
          <p style="word-break: break-all; color: #666;">${resetLink}</p>
          <div class="warning">This link will expire in <strong>1 hour</strong>.<br>If you didn't request this reset, you can safely ignore this email.</div>
        </div>
      </div>
    </body>
    </html>`;

    const text = `Hello ${username},\n\nReset your password: ${resetLink}\n\nThis link expires in 1 hour.`;

    try {
      await this.transporter!.sendMail({
        from: this.fromEmail,
        to: toEmail,
        subject: 'Practice Room - Password Reset Request',
        text,
        html,
      });
      console.log(`[EMAIL SERVICE] Password reset email sent to ${toEmail}`);
      return true;
    } catch (e) {
      console.error(`[EMAIL SERVICE] Failed to send email:`, e);
      console.log(
        `[EMAIL SERVICE] Token for ${username}: ${resetToken}`,
      );
      return false;
    }
  }

  async sendWelcomeEmail(
    toEmail: string,
    username: string,
  ): Promise<boolean> {
    if (!this.isConfigured()) {
      console.log(
        `[EMAIL SERVICE] Not configured. Welcome email for ${username}`,
      );
      return false;
    }

    const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }
        .button { display: inline-block; background: #405c68; color: #ffffff !important; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header"><h1>Welcome Aboard!</h1></div>
        <div class="content">
          <p>Hello <strong>${username}</strong>,</p>
          <p>Welcome to <strong>Practice Room</strong>! We are thrilled to have you join our community.</p>
          <p>Get started by exploring our practice modules and solving some challenges.</p>
          <p style="text-align: center;"><a href="${this.frontendUrl}" class="button" style="color: #ffffff; text-decoration: none;">Start Practicing</a></p>
          <p>Happy Coding!<br>Codebasics Team</p>
        </div>
      </div>
    </body>
    </html>`;

    const text = `Hello ${username},\n\nWelcome to Practice Room!\n\nGet started: ${this.frontendUrl}\n\nHappy Coding!\nThe Codebasics Team`;

    try {
      await this.transporter!.sendMail({
        from: this.fromEmail,
        to: toEmail,
        subject: 'Welcome to Practice Room!',
        text,
        html,
      });
      return true;
    } catch (e) {
      console.error(`[EMAIL SERVICE] Failed to send welcome email:`, e);
      return false;
    }
  }
}
