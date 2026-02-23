import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service.js';

/**
 * Converts a string to a URL-friendly slug.
 */
function slugify(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

function toPositiveInt(value: string): number | null {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed <= 0) return null;
  return parsed;
}

function normalizeDifficulty(value: string): 'easy' | 'medium' | 'hard' | null {
  const normalized = value.toLowerCase().trim();
  if (normalized === 'easy' || normalized === 'medium' || normalized === 'hard') {
    return normalized;
  }
  return null;
}

@Injectable()
export class ModulesService {
  constructor(private readonly prisma: PrismaService) { }

  async findAll() {
    return this.prisma.module.findMany({
      where: { is_active: true },
      orderBy: { created_at: 'asc' },
    });
  }

  async findBySlug(slug: string) {
    const mod = await this.prisma.module.findUnique({ where: { slug } });
    if (!mod || !mod.is_active) {
      throw new HttpException('Module not found', HttpStatus.NOT_FOUND);
    }
    return mod;
  }

  async findAllQuestions(filters?: { difficulty?: string; module_id?: string }) {
    const where: Record<string, any> = { is_active: true };

    if (filters?.difficulty) {
      const difficulty = normalizeDifficulty(filters.difficulty);
      if (difficulty) {
        where.difficulty = difficulty;
      }
    }
    if (filters?.module_id) {
      const moduleId = toPositiveInt(filters.module_id);
      if (moduleId) {
        where.module_id = moduleId;
      }
    }

    return this.prisma.moduleQuestion.findMany({
      where,
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

  async findQuestionsBySlug(
    slug: string,
    filters?: { difficulty?: string; topic?: string; search?: string },
  ) {
    const mod = await this.findBySlug(slug);

    const where: Record<string, any> = {
      module_id: mod.id,
      is_active: true,
    };

    if (filters?.difficulty) {
      const difficulty = normalizeDifficulty(filters.difficulty);
      if (difficulty) {
        where.difficulty = difficulty;
      }
    }
    if (filters?.topic) {
      where.topic = filters.topic;
    }
    if (filters?.search) {
      where.title = { contains: filters.search };
    }

    return this.prisma.moduleQuestion.findMany({
      where,
      orderBy: [{ difficulty: 'asc' }, { title: 'asc' }],
      select: {
        id: true,
        slug: true,
        title: true,
        difficulty: true,
        topic: true,
        tags: true,
        is_verified: true,
        created_at: true,
      },
    });
  }

  async findQuestionBySlug(moduleSlug: string, questionSlug: string) {
    const mod = await this.findBySlug(moduleSlug);

    const question = await this.prisma.moduleQuestion.findFirst({
      where: {
        module_id: mod.id,
        slug: questionSlug,
        is_active: true,
      },
    });

    if (!question) {
      throw new HttpException('Question not found', HttpStatus.NOT_FOUND);
    }

    return question;
  }

  async create(data: { name: string; description?: string }) {
    return this.prisma.module.create({
      data: {
        name: data.name,
        slug: slugify(data.name),
        description: data.description || null,
      },
    });
  }

  async update(moduleId: string, data: { name?: string; description?: string }) {
    const parsedModuleId = toPositiveInt(moduleId);
    if (!parsedModuleId) {
      throw new HttpException('Invalid module ID', HttpStatus.BAD_REQUEST);
    }

    const existing = await this.prisma.module.findUnique({ where: { id: parsedModuleId } });
    if (!existing) {
      throw new HttpException('Module not found', HttpStatus.NOT_FOUND);
    }

    const updateData: Record<string, any> = {};
    if (data.name !== undefined) {
      updateData.name = data.name;
      updateData.slug = slugify(data.name);
    }
    if (data.description !== undefined) updateData.description = data.description;

    return this.prisma.module.update({
      where: { id: parsedModuleId },
      data: updateData,
    });
  }

  async remove(moduleId: string) {
    const parsedModuleId = toPositiveInt(moduleId);
    if (!parsedModuleId) {
      throw new HttpException('Invalid module ID', HttpStatus.BAD_REQUEST);
    }

    const existing = await this.prisma.module.findUnique({ where: { id: parsedModuleId } });
    if (!existing) {
      throw new HttpException('Module not found', HttpStatus.NOT_FOUND);
    }

    // FK cascade will handle deleting related module_questions
    await this.prisma.module.delete({ where: { id: parsedModuleId } });
  }
}
