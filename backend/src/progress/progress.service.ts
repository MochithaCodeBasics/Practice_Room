import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service.js';

@Injectable()
export class ProgressService {
  constructor(private readonly prisma: PrismaService) {}

  async markCompleted(
    username: string,
    questionId: string,
    code?: string,
  ): Promise<void> {
    username = username.trim();
    questionId = questionId.trim();

    const existing = await this.prisma.userProgress.findUnique({
      where: { username_question_id: { username, question_id: questionId } },
    });

    const isNewCompletion = !existing || existing.status !== 'completed';

    await this.prisma.userProgress.upsert({
      where: { username_question_id: { username, question_id: questionId } },
      update: {
        status: 'completed',
        ...(code ? { user_code: code } : {}),
        updated_at: new Date(),
      },
      create: {
        username,
        question_id: questionId,
        status: 'completed',
        user_code: code || null,
      },
    });

    if (isNewCompletion) {
      await this.updateStreak(username);
    }
  }

  async markAttempted(
    username: string,
    questionId: string,
    code?: string,
  ): Promise<void> {
    username = username.trim();
    questionId = questionId.trim();

    const existing = await this.prisma.userProgress.findUnique({
      where: { username_question_id: { username, question_id: questionId } },
    });

    if (!existing) {
      await this.prisma.userProgress.create({
        data: {
          username,
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
    username: string,
  ): Promise<{ completed: Set<string>; attempted: Set<string> }> {
    username = username.trim();
    const records = await this.prisma.userProgress.findMany({
      where: { username },
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
    username: string,
    questionId: string,
  ): Promise<string | null> {
    username = username.trim();
    questionId = questionId.trim();

    const progress = await this.prisma.userProgress.findUnique({
      where: { username_question_id: { username, question_id: questionId } },
    });

    return progress?.user_code ?? null;
  }

  private async updateStreak(username: string): Promise<void> {
    await this.prisma.user.update({
      where: { username },
      data: {
        current_streak: { increment: 1 },
        last_completed_at: new Date(),
      },
    });
  }

  async refreshStreak(username: string): Promise<void> {
    const user = await this.prisma.user.findUnique({ where: { username } });
    if (!user || !user.last_completed_at) return;

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const lastDate = new Date(
      user.last_completed_at.getFullYear(),
      user.last_completed_at.getMonth(),
      user.last_completed_at.getDate(),
    );

    const diffDays =
      (today.getTime() - lastDate.getTime()) / (1000 * 60 * 60 * 24);

    if (diffDays > 1) {
      await this.prisma.user.update({
        where: { username },
        data: { current_streak: 0 },
      });
    }
  }
}
