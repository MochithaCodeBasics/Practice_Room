import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service.js';

@Injectable()
export class ProgressService {
  constructor(private readonly prisma: PrismaService) {}

  async markCompleted(
    userId: number,
    questionId: string,
    code?: string,
  ): Promise<void> {
    questionId = questionId.trim();

    await this.prisma.userProgress.upsert({
      where: { user_id_question_id: { user_id: userId, question_id: questionId } },
      update: {
        status: 'completed',
        ...(code ? { user_code: code } : {}),
        updated_at: new Date(),
      },
      create: {
        user_id: userId,
        question_id: questionId,
        status: 'completed',
        user_code: code || null,
      },
    });
  }

  async markAttempted(
    userId: number,
    questionId: string,
    code?: string,
  ): Promise<void> {
    questionId = questionId.trim();

    const existing = await this.prisma.userProgress.findUnique({
      where: { user_id_question_id: { user_id: userId, question_id: questionId } },
    });

    if (!existing) {
      await this.prisma.userProgress.create({
        data: {
          user_id: userId,
          question_id: questionId,
          status: 'attempted',
          user_code: code || null,
        },
      });
    } else {
      // Preserve completed status
      await this.prisma.userProgress.update({
        where: { id: existing.id },
        data: {
          ...(existing.status !== 'completed' ? { status: 'attempted' } : {}),
          user_code: code ?? existing.user_code,
          updated_at: new Date(),
        },
      });
    }
  }

  async getProgress(
    userId: number,
  ): Promise<{ completed: Set<string>; attempted: Set<string> }> {
    const records = await this.prisma.userProgress.findMany({
      where: { user_id: userId },
    });

    const completed = new Set<string>();
    const attempted = new Set<string>();

    for (const p of records) {
      const qid = p.question_id.trim();
      if (p.status === 'completed') {
        completed.add(qid);
      } else if (p.status === 'attempted') {
        attempted.add(qid);
      }
    }

    return { completed, attempted };
  }

  async getUserCode(
    userId: number,
    questionId: string,
  ): Promise<string | null> {
    questionId = questionId.trim();

    const progress = await this.prisma.userProgress.findUnique({
      where: { user_id_question_id: { user_id: userId, question_id: questionId } },
    });

    return progress?.user_code ?? null;
  }
}
