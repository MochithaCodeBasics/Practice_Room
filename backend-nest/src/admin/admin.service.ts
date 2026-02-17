import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as fs from 'fs';
import * as path from 'path';
import { PrismaService } from '../prisma/prisma.service.js';

@Injectable()
export class AdminService {
  private questionsDir: string;

  constructor(
    private readonly prisma: PrismaService,
    private readonly config: ConfigService,
  ) {
    this.questionsDir = this.config.get<string>('questionsDir')!;
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
    const maxRetries = 3;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        // Determine next ID
        const existingQuestions = await this.prisma.question.findMany({
          select: { id: true },
        });

        let maxNum = 0;
        for (const q of existingQuestions) {
          const match = q.id.match(/\d+/);
          if (match) {
            const num = parseInt(match[0]);
            if (num > maxNum) maxNum = num;
          }
        }

        const newIdNum = maxNum + 1;
        const newId = `q${newIdNum}`;
        const folderName = `question_${String(newIdNum).padStart(2, '0')}`;
        const folderPath = path.join(this.questionsDir, folderName);

        if (fs.existsSync(folderPath)) {
          throw new HttpException(
            `Directory ${folderName} already exists but DB record missing.`,
            HttpStatus.INTERNAL_SERVER_ERROR,
          );
        }

        fs.mkdirSync(folderPath, { recursive: true });

        try {
          // Save question.py
          if (data.questionPyFile) {
            fs.writeFileSync(
              path.join(folderPath, 'question.py'),
              data.questionPyFile.buffer,
            );
          } else if (data.questionPyContent) {
            fs.writeFileSync(
              path.join(folderPath, 'question.py'),
              data.questionPyContent,
              'utf-8',
            );
          }

          // Save validator.py
          if (data.validatorPyFile) {
            fs.writeFileSync(
              path.join(folderPath, 'validator.py'),
              data.validatorPyFile.buffer,
            );
          } else if (data.validatorPyContent) {
            fs.writeFileSync(
              path.join(folderPath, 'validator.py'),
              data.validatorPyContent,
              'utf-8',
            );
          }

          // Save data files
          if (data.dataFiles) {
            for (const file of data.dataFiles) {
              if (file.originalname) {
                const safeName = path.basename(file.originalname);
                fs.writeFileSync(
                  path.join(folderPath, safeName),
                  file.buffer,
                );
              }
            }
          }

          // Save inline data file
          if (data.dataFileContent && data.dataFileName) {
            const safeName = path.basename(data.dataFileName);
            fs.writeFileSync(
              path.join(folderPath, safeName),
              data.dataFileContent,
              'utf-8',
            );
          }
        } catch (e: any) {
          // Cleanup on failure
          if (fs.existsSync(folderPath)) {
            fs.rmSync(folderPath, { recursive: true, force: true });
          }
          throw new HttpException(
            `Failed to save files: ${e.message}`,
            HttpStatus.INTERNAL_SERVER_ERROR,
          );
        }

        // Save to DB
        await this.prisma.question.create({
          data: {
            id: newId,
            folder_name: folderName,
            title: data.title,
            difficulty: data.difficulty,
            module_id: data.module_id,
            topic: data.topic || 'General',
            tags: data.tags || '',
          },
        });

        return {
          message: 'Question created successfully',
          id: newId,
          folder: folderName,
        };
      } catch (e: any) {
        if (e.code === 'P2002' && attempt < maxRetries - 1) {
          // Prisma unique constraint violation — retry
          await new Promise((r) =>
            setTimeout(r, 100 + Math.random() * 200),
          );
          continue;
        }
        throw e;
      }
    }

    throw new HttpException(
      'Could not generate unique Question ID after retries.',
      HttpStatus.INTERNAL_SERVER_ERROR,
    );
  }

  async deleteQuestion(questionId: string) {
    const question = await this.prisma.question.findUnique({
      where: { id: questionId },
    });
    if (!question) {
      throw new HttpException('Question not found', HttpStatus.NOT_FOUND);
    }

    const folderPath = path.join(this.questionsDir, question.folder_name);

    // Delete progress records first
    await this.prisma.userProgress.deleteMany({
      where: { question_id: questionId },
    });

    await this.prisma.question.delete({ where: { id: questionId } });

    if (fs.existsSync(folderPath)) {
      try {
        fs.rmSync(folderPath, { recursive: true, force: true });
      } catch (e) {
        console.error(`Error deleting directory ${folderPath}:`, e);
      }
    }
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
    const question = await this.prisma.question.findUnique({
      where: { id: questionId },
    });
    if (!question) {
      throw new HttpException('Question not found', HttpStatus.NOT_FOUND);
    }

    const folderPath = path.join(this.questionsDir, question.folder_name);

    // Update metadata
    const updateData: any = {};
    if (data.title !== undefined) updateData.title = data.title;
    if (data.difficulty !== undefined)
      updateData.difficulty = data.difficulty;
    if (data.topic !== undefined) updateData.topic = data.topic;
    if (data.tags !== undefined) updateData.tags = data.tags;

    // Replace files if provided
    try {
      if (data.questionPyFile?.originalname) {
        fs.writeFileSync(
          path.join(folderPath, 'question.py'),
          data.questionPyFile.buffer,
        );
      }
      if (data.validatorPyFile?.originalname) {
        fs.writeFileSync(
          path.join(folderPath, 'validator.py'),
          data.validatorPyFile.buffer,
        );
      }
      if (data.dataFiles) {
        for (const file of data.dataFiles) {
          if (file.originalname) {
            const safeName = path.basename(file.originalname);
            fs.writeFileSync(
              path.join(folderPath, safeName),
              file.buffer,
            );
          }
        }
      }
    } catch (e: any) {
      throw new HttpException(
        `Failed to update files: ${e.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }

    await this.prisma.question.update({
      where: { id: questionId },
      data: updateData,
    });

    return { message: 'Question updated successfully', id: questionId };
  }

  async verifyQuestion(questionId: string, verified: boolean) {
    const question = await this.prisma.question.findUnique({
      where: { id: questionId },
    });
    if (!question) {
      throw new HttpException('Question not found', HttpStatus.NOT_FOUND);
    }

    await this.prisma.question.update({
      where: { id: questionId },
      data: { is_verified: verified },
    });

    return {
      message: `Question verification status set to ${verified}`,
      id: questionId,
      is_verified: verified,
    };
  }
}
