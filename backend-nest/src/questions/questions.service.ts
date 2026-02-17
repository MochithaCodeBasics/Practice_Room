import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as fs from 'fs';
import * as path from 'path';
import { PrismaService } from '../prisma/prisma.service.js';
import { ProgressService } from '../progress/progress.service.js';

@Injectable()
export class QuestionsService {
  private questionsDir: string;

  constructor(
    private readonly prisma: PrismaService,
    private readonly config: ConfigService,
    private readonly progressService: ProgressService,
  ) {
    this.questionsDir = this.config.get<string>('questionsDir')!;
  }

  async getAllQuestions(
    username?: string,
    difficulty?: string,
    status?: string,
    userRole?: string,
  ) {
    const userProgress = username
      ? await this.progressService.getProgress(username)
      : { completed: new Set<string>(), attempted: new Set<string>() };

    const where: any = {};
    if (difficulty) where.difficulty = difficulty;

    const questions = await this.prisma.question.findMany({ where });

    const result: any[] = [];
    for (const q of questions) {
      // Hide unverified from non-admins
      if (!q.is_verified && userRole !== 'admin') continue;

      const qid = q.id.trim();
      const isCompleted = userProgress.completed.has(qid);
      const isAttempted = userProgress.attempted.has(qid);

      // Apply status filter
      if (status === 'completed' && !isCompleted) continue;
      if (status === 'attempted' && !(isAttempted && !isCompleted)) continue;
      if (status === 'todo' && (isCompleted || isAttempted)) continue;

      result.push({
        id: q.id,
        folder_name: q.folder_name,
        title: q.title,
        module_id: q.module_id,
        difficulty: q.difficulty,
        topic: q.topic,
        tags: q.tags,
        is_verified: q.is_verified,
        is_completed: isCompleted,
        is_attempted: isAttempted,
        created_at: q.created_at,
      });
    }

    return result;
  }

  async getQuestion(
    questionId: string,
    username?: string,
    userRole?: string,
  ) {
    const question = await this.prisma.question.findUnique({
      where: { id: questionId },
    });
    if (!question) return null;

    const folderPath = path.join(this.questionsDir, question.folder_name);
    if (!fs.existsSync(folderPath)) return null;

    // Read files from disk
    const qFile = path.join(folderPath, 'question.py');
    const vFile = path.join(folderPath, 'validator.py');

    const qText = fs.existsSync(qFile)
      ? fs.readFileSync(qFile, 'utf-8')
      : '';
    const vText = fs.existsSync(vFile)
      ? fs.readFileSync(vFile, 'utf-8')
      : '';

    // Extract metadata from question.py using triple-quote parser
    const description =
      this.extractStr(qText, 'description') || 'Description not found.';
    let initialCode =
      this.extractStr(qText, 'initial_sample_code') ||
      this.extractStr(qText, 'inital_sample_code') ||
      '# No starting code provided.';
    const hint = this.extractStr(qText, 'hint')?.trim() || null;

    // Get sample data
    const sampleData = this.getSampleData(folderPath, question.folder_name);

    // List data files
    const dataFiles = fs.existsSync(folderPath)
      ? fs
          .readdirSync(folderPath)
          .filter(
            (f) =>
              (f.endsWith('.csv') ||
                f.endsWith('.txt') ||
                f.endsWith('.json')) &&
              f !== 'master_question_list.csv',
          )
      : [];

    // User progress
    const userProgress = username
      ? await this.progressService.getProgress(username)
      : { completed: new Set<string>(), attempted: new Set<string>() };

    // Load saved code if available
    const shouldLoadProgress =
      !(userRole === 'admin' && !question.is_verified);
    if (username && shouldLoadProgress) {
      const savedCode = await this.progressService.getUserCode(
        username,
        questionId,
      );
      if (savedCode) {
        initialCode = savedCode;
      }
    }

    const qid = question.id.trim();
    return {
      id: question.id,
      folder_name: question.folder_name,
      title: question.title,
      module_id: question.module_id,
      difficulty: question.difficulty,
      topic: question.topic,
      tags: question.tags,
      question_py: description.trim(),
      initial_code: initialCode,
      validator_py: vText,
      hint,
      sample_data: sampleData || '',
      data_files: dataFiles,
      is_verified: question.is_verified,
      is_completed: userProgress.completed.has(qid),
      is_attempted: userProgress.attempted.has(qid),
    };
  }

  private extractStr(source: string, varName: string): string | null {
    const startMarker = `${varName} = """`;
    const start = source.indexOf(startMarker);
    if (start === -1) return null;
    const contentStart = start + startMarker.length;
    const end = source.indexOf('"""', contentStart);
    if (end === -1) return null;
    return source.substring(contentStart, end);
  }

  private getSampleData(
    folderPath: string,
    folderName: string,
  ): string | null {
    let previewFile: string | null = null;

    for (const ext of ['csv', 'txt']) {
      for (const name of ['data', 'sales', folderName]) {
        const f = path.join(folderPath, `${name}.${ext}`);
        if (fs.existsSync(f)) {
          previewFile = f;
          break;
        }
      }
      if (previewFile) break;
    }

    if (!previewFile) return null;

    try {
      if (previewFile.endsWith('.csv')) {
        const content = fs.readFileSync(previewFile, 'utf-8');
        const lines = content.split('\n').filter((l) => l.trim());
        const rows = lines.slice(0, 6).map((l) => l.split(','));

        if (rows.length === 0) return null;

        const headers = rows[0];
        const data = rows.slice(1);

        let md = '| ' + headers.join(' | ') + ' |\n';
        md += '| ' + headers.map(() => '---').join(' | ') + ' |\n';
        for (const row of data) {
          md += '| ' + row.join(' | ') + ' |\n';
        }
        return md;
      } else {
        const content = fs.readFileSync(previewFile, 'utf-8');
        const lines = content.split('\n').slice(0, 5);
        return '```\n' + lines.join('\n') + '\n```';
      }
    } catch {
      return null;
    }
  }
}
