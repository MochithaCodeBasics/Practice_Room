import { IsNotEmpty, IsString, MinLength } from 'class-validator';

export class ChangePasswordDto {
    @IsString()
    @IsNotEmpty()
    current_password: string;

    @IsString()
    @IsNotEmpty()
    @MinLength(8, { message: 'New password must be at least 8 characters long' })
    new_password: string;
}
