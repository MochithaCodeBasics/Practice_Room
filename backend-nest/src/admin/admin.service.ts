import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as fs from 'fs';
import * as path from 'path';
import { PrismaService } from '../prisma/prisma.service.js';

function toPositiveInt(value: string): number | null {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed <= 0) return null;
  return parsed;
}

function normalizeDifficulty(
  value: string,
): 'easy' | 'medium' | 'hard' | null {
  const normalized = value.toLowerCase().trim();
  if (
    normalized === 'easy' ||
    normalized === 'medium' ||
    normalized === 'hard'
  ) {
    return normalized;
  }
  return null;
}

function slugify(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

@Injectable()
export class AdminService {
  private questionsDir: string;

  constructor(
    private readonly prisma: PrismaService,
    private readonly config: ConfigService,
  ) {
    this.questionsDir = this.config.get<string>('questionsDir')!;
  }

  private getTemplatePath(type: 'question' | 'validator') {
    const templatesDir = path.join(this.questionsDir, 'templates');
    const fileName =
      type === 'question' ? 'question_template.py' : 'validator_template.py';
    return {
      fileName,
      fullPath: path.join(templatesDir, fileName),
    };
  }

  async getTemplate(type: 'question' | 'validator') {
    const { fileName, fullPath } = this.getTemplatePath(type);
    if (!fs.existsSync(fullPath)) {
      throw new HttpException(
        `Template not found: ${fileName}`,
        HttpStatus.NOT_FOUND,
      );
    }

    return {
      type,
      file_name: fileName,
      content: fs.readFileSync(fullPath, 'utf-8'),
    };
  }

  async getAllTemplates() {
    const [question, validator] = await Promise.all([
      this.getTemplate('question'),
      this.getTemplate('validator'),
    ]);

    return {
      templates: [question, validator],
    };
  }

  private extractPyVar(content: string, varName: string): string | null {
    const regex = new RegExp(
      `${varName}\\s*=\\s*(?:"""([\\s\\S]*?)"""|'''([\\s\\S]*?)''')`,
    );
    const match = content.match(regex);
    if (!match) return null;
    return (match[1] ?? match[2] ?? '').trim();
  }

  private parseQuestionPy(content: string): {
    description: string | null;
    initialCode: string | null;
    hint: string | null;
  } {
    return {
      description: this.extractPyVar(content, 'description'),
      initialCode:
        this.extractPyVar(content, 'initial_sample_code') ??
        this.extractPyVar(content, 'inital_sample_code'),
      hint: this.extractPyVar(content, 'hint'),
    };
  }

  private toUtf8(file?: Express.Multer.File, inline?: string): string | null {
    if (file?.buffer) return file.buffer.toString('utf-8');
    if (inline) return inline;
    return null;
  }

  async createQuestion(data: {
    title: string;
    difficulty: string;
    module_id: string;
    tags?: string;
    topic?: string;
    questionPyContent?: string;
    questionPyFile?: Express.Multer.File;
    validatorPyContent?: string;
    validatorPyFile?: Express.Multer.File;
    dataFiles?: Express.Multer.File[];
    dataFileContent?: string;
    dataFileName?: string;
  }) {
    const title = data.title?.trim();
    if (!title) {
      throw new HttpException('Question title is required', HttpStatus.BAD_REQUEST);
    }

    const moduleId = toPositiveInt(data.module_id);
    if (!moduleId) {
      throw new HttpException('Invalid module_id', HttpStatus.BAD_REQUEST);
    }

    const module = await this.prisma.module.findUnique({ where: { id: moduleId } });
    if (!module) {
      throw new HttpException('Module not found', HttpStatus.BAD_REQUEST);
    }

    const difficulty = normalizeDifficulty(data.difficulty);
    if (!difficulty) {
      throw new HttpException('Invalid difficulty', HttpStatus.BAD_REQUEST);
    }

    const questionPyContent = this.toUtf8(
      data.questionPyFile,
      data.questionPyContent,
    );
    const validatorPyContent = this.toUtf8(
      data.validatorPyFile,
      data.validatorPyContent,
    );

    if (!questionPyContent) {
      throw new HttpException(
        'question.py file content is required',
        HttpStatus.BAD_REQUEST,
      );
    }
    if (!validatorPyContent) {
      throw new HttpException(
        'validator.py file content is required',
        HttpStatus.BAD_REQUEST,
      );
    }

    const parsed = questionPyContent
      ? this.parseQuestionPy(questionPyContent)
      : { description: null, initialCode: null, hint: null };
    let sampleData = data.dataFileContent ?? null;
    if (!sampleData && data.dataFiles?.length) {
      for (const file of data.dataFiles) {
        const safeName = (file.originalname || '').toLowerCase();
        if (safeName.endsWith('.csv') || safeName.endsWith('.txt')) {
          sampleData = file.buffer.toString('utf-8');
          break;
        }
      }
    }
    const folderName = `db_${slugify(title)}_${Date.now()}`.slice(0, 100);

    try {
      const created = await this.prisma.moduleQuestion.create({
        data: {
          module_id: moduleId,
          slug: slugify(title),
          folder_name: folderName,
          title,
          difficulty,
          topic: data.topic || 'General',
          tags: data.tags || '',
          question_py: parsed.description,
          initial_code: parsed.initialCode,
          hint: parsed.hint,
          validator_py: validatorPyContent,
          sample_data: sampleData,
        },
      });

      return {
        message: 'Question created successfully',
        id: String(created.id),
        folder: null,
      };
    } catch (e: any) {
      if (e?.code === 'P2002') {
        throw new HttpException(
          'A question with the same title/slug already exists in this module',
          HttpStatus.CONFLICT,
        );
      }
      if (e?.code === 'P2003') {
        throw new HttpException(
          'Invalid module reference',
          HttpStatus.BAD_REQUEST,
        );
      }
      throw new HttpException(
        e?.message || 'Failed to create question',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  async getQuestions() {
    return this.prisma.moduleQuestion.findMany({
      orderBy: [{ created_at: 'desc' }, { title: 'asc' }],
      select: {
        id: true,
        slug: true,
        title: true,
        module_id: true,
        difficulty: true,
        topic: true,
        tags: true,
        is_verified: true,
        created_at: true,
      },
    });
  }

  async deleteQuestion(questionId: string) {
    const parsedQuestionId = toPositiveInt(questionId);
    if (!parsedQuestionId) {
      throw new HttpException('Invalid question ID', HttpStatus.BAD_REQUEST);
    }

    const question = await this.prisma.moduleQuestion.findUnique({
      where: { id: parsedQuestionId },
    });
    if (!question) {
      throw new HttpException('Question not found', HttpStatus.NOT_FOUND);
    }

    // Delete progress records first
    await this.prisma.userProgress.deleteMany({
      where: { question_id: String(parsedQuestionId) },
    });

    await this.prisma.moduleQuestion.delete({ where: { id: parsedQuestionId } });
  }

  async updateQuestion(
    questionId: string,
    data: {
      title?: string;
      difficulty?: string;
      topic?: string;
      tags?: string;
      questionPyFile?: Express.Multer.File;
      validatorPyFile?: Express.Multer.File;
      dataFiles?: Express.Multer.File[];
    },
  ) {
    const parsedQuestionId = toPositiveInt(questionId);
    if (!parsedQuestionId) {
      throw new HttpException('Invalid question ID', HttpStatus.BAD_REQUEST);
    }

    const question = await this.prisma.moduleQuestion.findUnique({
      where: { id: parsedQuestionId },
    });
    if (!question) {
      throw new HttpException('Question not found', HttpStatus.NOT_FOUND);
    }

    const folderPath = path.join(this.questionsDir, question.folder_name);

    // Update metadata
    const updateData: any = {};
    if (data.title !== undefined) updateData.title = data.title;
    if (data.difficulty !== undefined) {
      const difficulty = normalizeDifficulty(data.difficulty);
      if (!difficulty) {
        throw new HttpException('Invalid difficulty', HttpStatus.BAD_REQUEST);
      }
      updateData.difficulty = difficulty;
    }
    if (data.topic !== undefined) updateData.topic = data.topic;
    if (data.tags !== undefined) updateData.tags = data.tags;

    // Replace files if provided
    try {
      if (data.questionPyFile?.originalname) {
        const questionPyContent = data.questionPyFile.buffer.toString('utf-8');
        fs.writeFileSync(
          path.join(folderPath, 'question.py'),
          questionPyContent,
          'utf-8',
        );
        const parsed = this.parseQuestionPy(questionPyContent);
        updateData.question_py = parsed.description;
        updateData.initial_code = parsed.initialCode;
        updateData.hint = parsed.hint;
      }
      if (data.validatorPyFile?.originalname) {
        const validatorContent = data.validatorPyFile.buffer.toString('utf-8');
        fs.writeFileSync(
          path.join(folderPath, 'validator.py'),
          validatorContent,
          'utf-8',
        );
        updateData.validator_py = validatorContent;
      }
      if (data.dataFiles) {
        for (const file of data.dataFiles) {
          if (file.originalname) {
            const safeName = path.basename(file.originalname);
            fs.writeFileSync(
              path.join(folderPath, safeName),
              file.buffer,
            );
            if (!updateData.sample_data && (safeName.endsWith('.csv') || safeName.endsWith('.txt'))) {
              updateData.sample_data = file.buffer.toString('utf-8');
            }
          }
        }
      }
    } catch (e: any) {
      throw new HttpException(
        `Failed to update files: ${e.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }

    await this.prisma.moduleQuestion.update({
      where: { id: parsedQuestionId },
      data: updateData,
    });

    return { message: 'Question updated successfully', id: String(parsedQuestionId) };
  }

  async verifyQuestion(questionId: string, verified: boolean) {
    const parsedQuestionId = toPositiveInt(questionId);
    if (!parsedQuestionId) {
      throw new HttpException('Invalid question ID', HttpStatus.BAD_REQUEST);
    }

    const question = await this.prisma.moduleQuestion.findUnique({
      where: { id: parsedQuestionId },
    });
    if (!question) {
      throw new HttpException('Question not found', HttpStatus.NOT_FOUND);
    }

    await this.prisma.moduleQuestion.update({
      where: { id: parsedQuestionId },
      data: { is_verified: verified },
    });

    return {
      message: `Question verification status set to ${verified}`,
      id: String(parsedQuestionId),
      is_verified: verified,
    };
  }
}
