import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as fs from 'fs';
import * as path from 'path';
import { PrismaService } from '../prisma/prisma.service.js';
import { ProgressService } from '../progress/progress.service.js';

function toPositiveInt(value: string): number | null {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed <= 0) return null;
  return parsed;
}

function normalizeDifficulty(value?: string): 'easy' | 'medium' | 'hard' | null {
  if (!value) return null;
  const normalized = value.toLowerCase().trim();
  if (normalized === 'easy' || normalized === 'medium' || normalized === 'hard') {
    return normalized;
  }
  return null;
}

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
    userId?: number,
    difficulty?: string,
    status?: string,
    userRole?: string,
  ) {
    const userProgress = userId
      ? await this.progressService.getProgress(userId)
      : { completed: new Set<string>(), attempted: new Set<string>() };

    const where: any = { is_active: true };
    const normalizedDifficulty = normalizeDifficulty(difficulty);
    if (normalizedDifficulty) where.difficulty = normalizedDifficulty;

    const questions = await this.prisma.moduleQuestion.findMany({ where });

    const result: any[] = [];
    for (const q of questions) {
      // Hide unverified from non-admins
      if (!q.is_verified && userRole !== 'admin') continue;

      const qid = String(q.id);
      const isCompleted = userProgress.completed.has(qid);
      const isAttempted = userProgress.attempted.has(qid);

      // Apply status filter
      if (status === 'completed' && !isCompleted) continue;
      if (status === 'attempted' && !(isAttempted && !isCompleted)) continue;
      if (status === 'todo' && (isCompleted || isAttempted)) continue;

      result.push({
        id: String(q.id),
        folder_name: q.folder_name,
        title: q.title,
        module_id: String(q.module_id),
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
    userId?: number,
    userRole?: string,
  ) {
    const parsedQuestionId = toPositiveInt(questionId);
    if (!parsedQuestionId) return null;

    const question = await this.prisma.moduleQuestion.findUnique({
      where: { id: parsedQuestionId },
    });
    if (!question) return null;
    if (!question.is_active && userRole !== 'admin') return null;

    const folderPath = path.join(this.questionsDir, question.folder_name);

    // Guard against path traversal via DB-stored folder_name
    if (
      !path.resolve(folderPath).startsWith(
        path.resolve(this.questionsDir) + path.sep,
      )
    ) {
      return null;
    }

    const hasFolder = fs.existsSync(folderPath);

    // Read files from disk
    const qFile = path.join(folderPath, 'question.py');
    const vFile = path.join(folderPath, 'validator.py');

    const qText = hasFolder && fs.existsSync(qFile)
      ? fs.readFileSync(qFile, 'utf-8')
      : '';
    const vText = hasFolder && fs.existsSync(vFile)
      ? fs.readFileSync(vFile, 'utf-8')
      : '';

    // Prefer DB fields; fallback to file parsing for legacy questions.
    const description =
      question.question_py ||
      this.extractStr(qText, 'description') ||
      'Description not found.';
    let initialCode =
      question.initial_code ||
      this.extractStr(qText, 'initial_sample_code') ||
      this.extractStr(qText, 'inital_sample_code') ||
      '# No starting code provided.';
    const hint =
      question.hint ||
      this.extractStr(qText, 'hint')?.trim() ||
      null;

    // Get sample data and ensure it's in markdown table format
    const rawSampleData =
      question.sample_data || this.getSampleData(folderPath, question.folder_name);
    const sampleData = rawSampleData ? this.ensureMarkdownTable(rawSampleData) : null;

    // List data files
    const dataFiles = hasFolder
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
    const userProgress = userId
      ? await this.progressService.getProgress(userId)
      : { completed: new Set<string>(), attempted: new Set<string>() };

    // Load saved code if available
    const shouldLoadProgress =
      !(userRole === 'admin' && !question.is_verified);
    if (userId && shouldLoadProgress) {
      const savedCode = await this.progressService.getUserCode(
        userId,
        String(question.id),
      );
      if (savedCode) {
        initialCode = savedCode;
      }
    }

    const qid = String(question.id);
    return {
      id: String(question.id),
      folder_name: question.folder_name,
      title: question.title,
      module_id: String(question.module_id),
      difficulty: question.difficulty,
      topic: question.topic,
      tags: question.tags,
      question_py: description.trim(),
      initial_code: initialCode,
      validator_py: question.validator_py || vText,
      hint,
      sample_data: sampleData || '',
      data_files: dataFiles,
      is_active: question.is_active,
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

  private ensureMarkdownTable(data: string): string {
    const trimmed = data.trim();
    // Already a markdown table or fenced code block — pass through as-is
    if (trimmed.startsWith('|') || trimmed.startsWith('`')) return trimmed;
    // Raw text/CSV: wrap in a fenced code block so newlines are preserved
    const lines = trimmed.split('\n').filter((l) => l.trim()).slice(0, 10);
    return '```\n' + lines.join('\n') + '\n```';
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
