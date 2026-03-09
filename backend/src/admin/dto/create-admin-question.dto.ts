import { IsIn, IsNotEmpty, IsOptional, IsString } from 'class-validator';

export class CreateAdminQuestionDto {
  @IsString()
  @IsNotEmpty()
  title: string;

  @IsString()
  @IsNotEmpty()
  module_id: string;

  @IsString()
  @IsIn(['easy', 'medium', 'hard', 'Easy', 'Medium', 'Hard'])
  difficulty: string;

  @IsOptional()
  @IsString()
  topic?: string;

  @IsOptional()
  @IsString()
  tags?: string;

  @IsOptional()
  @IsString()
  question_text?: string;

  @IsOptional()
  @IsString()
  validator_text?: string;

  @IsOptional()
  @IsString()
  sample_data?: string;

  @IsOptional()
  @IsString()
  data_file_content?: string;

  @IsOptional()
  @IsString()
  data_file_name?: string;
}
