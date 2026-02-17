import { IsOptional, IsString } from 'class-validator';

export class UserSettingsDto {
  @IsOptional()
  @IsString()
  groq_api_key?: string;

  @IsOptional()
  @IsString()
  openai_api_key?: string;

  @IsOptional()
  @IsString()
  anthropic_api_key?: string;

  @IsOptional()
  @IsString()
  default_llm_provider?: string;
}
