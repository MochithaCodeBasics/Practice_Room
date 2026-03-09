import { IsEmail, IsString, MinLength } from 'class-validator';

export class PasswordResetRequestDto {
  @IsEmail()
  email: string;
}

export class PasswordResetVerifyDto {
  @IsString()
  token: string;

  @IsString()
  @MinLength(8)
  new_password: string;
}
