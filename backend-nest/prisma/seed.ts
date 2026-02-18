import 'dotenv/config';
import { PrismaMariaDb } from '@prisma/adapter-mariadb';
import { PrismaClient } from '../generated/prisma/client.js';
import * as fs from 'fs';
import * as path from 'path';

// ─── Database connection ─────────────────────────────────────────────────────
const connectionString = `mariadb://${process.env.DB_USER}:${process.env.DB_PASSWORD}@${process.env.DB_HOST}:${process.env.DB_PORT}/${process.env.DB_NAME}`;
const adapter = new PrismaMariaDb(connectionString);
const prisma = new PrismaClient({ adapter });

// ─── Helpers ─────────────────────────────────────────────────────────────────

function slugify(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

/**
 * Extracts the value of a Python triple-quoted variable from a .py file.
 * e.g. `description = """..."""` → returns the string between triple quotes.
 */
function extractPyVar(content: string, varName: string): string | null {
  // Match: varName = """...""" or varName = '''...'''
  const regex = new RegExp(
    `${varName}\\s*=\\s*(?:"""([\\s\\S]*?)"""|'''([\\s\\S]*?)''')`,
  );
  const match = content.match(regex);
  if (match) {
    return (match[1] ?? match[2] ?? '').trim();
  }
  return null;
}

/**
 * Parses a simple CSV string into an array of objects.
 * Handles quoted fields containing commas.
 */
function parseCSV(content: string): Record<string, string>[] {
  const lines = content.trim().split('\n');
  if (lines.length < 2) return [];

  const headers = lines[0].split(',').map((h) => h.trim());
  const rows: Record<string, string>[] = [];

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    // Parse CSV fields handling quoted values
    const fields: string[] = [];
    let current = '';
    let inQuotes = false;

    for (const char of line) {
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        fields.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }
    fields.push(current.trim());

    const row: Record<string, string> = {};
    headers.forEach((h, idx) => {
      row[h] = fields[idx] ?? '';
    });
    rows.push(row);
  }

  return rows;
}

// ─── Module seed data ────────────────────────────────────────────────────────

interface ModuleSeed {
  key: string;
  name: string;
  description?: string;
}

const MODULES: ModuleSeed[] = [
  {
    key: 'python',
    name: 'Python',
    description: 'Master Python with hands-on coding challenges',
  },
];

const seededModuleIds = new Map<string, number>();

// ─── Seed modules ────────────────────────────────────────────────────────────

async function seedModules() {
  console.log('Seeding modules...');
  seededModuleIds.clear();

  for (const mod of MODULES) {
    const slug = slugify(mod.name);

    await prisma.module.upsert({
      where: { slug },
      update: {
        name: mod.name,
        slug,
        description: mod.description ?? null,
      },
      create: {
        name: mod.name,
        slug,
        description: mod.description ?? null,
      },
    });

    const moduleRecord = await prisma.module.findUnique({
      where: { slug },
      select: { id: true },
    });
    if (!moduleRecord) {
      throw new Error(`Failed to resolve module id for slug "${slug}"`);
    }
    seededModuleIds.set(mod.key, moduleRecord.id);

    console.log(
      `  ✓ Module "${mod.name}" (key: ${mod.key}, id: ${moduleRecord.id}, slug: ${slug})`,
    );
  }

  console.log(`Seeded ${MODULES.length} module(s)\n`);
}

// ─── Seed questions ──────────────────────────────────────────────────────────

async function seedQuestions() {
  console.log('Seeding questions...');

  // Resolve paths: seed is run from backend-nest root via `npx prisma db seed`
  const projectRoot = process.cwd();
  const questionsDir = path.resolve(projectRoot, '..', 'questions');
  const csvPath = path.join(questionsDir, 'master_question_list.csv');

  if (!fs.existsSync(csvPath)) {
    console.log(`  ⚠ CSV not found at ${csvPath}, skipping question seeding.`);
    return;
  }

  const csvContent = fs.readFileSync(csvPath, 'utf-8');
  const rows = parseCSV(csvContent);

  console.log(`  Found ${rows.length} question(s) in CSV\n`);

  let seeded = 0;
  let skipped = 0;

  for (const row of rows) {
    const legacyQuestionId = row['id'];
    const folderName = row['folder_name'];
    const title = row['title'];
    const difficulty = (row['difficulty'] || 'easy').toLowerCase() as 'easy' | 'medium' | 'hard';
    const tags = row['tags'] || null;
    const active = row['active'] !== 'False';
    const topic = row['topic'] || 'General';
    const moduleKey = row['module_id'];

    if (!folderName || !title || !moduleKey) {
      console.log(`  ⚠ Skipping row — missing required fields: ${JSON.stringify(row)}`);
      skipped++;
      continue;
    }

    // Only seed questions belonging to seeded modules
    const moduleId = seededModuleIds.get(moduleKey);
    if (!moduleId) {
      console.log(
        `  ⊘ Skipping "${legacyQuestionId || title}" — module "${moduleKey}" not seeded`,
      );
      skipped++;
      continue;
    }

    const questionDir = path.join(questionsDir, folderName);
    if (!fs.existsSync(questionDir)) {
      console.log(
        `  ⚠ Skipping "${legacyQuestionId || title}" — folder not found: ${questionDir}`,
      );
      skipped++;
      continue;
    }

    // Read question.py → extract description, hint, initial_sample_code
    let questionPy: string | null = null;
    let hint: string | null = null;
    let initialCode: string | null = null;

    const questionPyPath = path.join(questionDir, 'question.py');
    if (fs.existsSync(questionPyPath)) {
      const pyContent = fs.readFileSync(questionPyPath, 'utf-8');
      questionPy = extractPyVar(pyContent, 'description');
      hint = extractPyVar(pyContent, 'hint');
      initialCode = extractPyVar(pyContent, 'initial_sample_code');
    }

    // Read validator.py → store full content
    let validatorPy: string | null = null;
    const validatorPath = path.join(questionDir, 'validator.py');
    if (fs.existsSync(validatorPath)) {
      validatorPy = fs.readFileSync(validatorPath, 'utf-8');
    }

    // Read sample data → data.csv or any other data file (e.g. sales.txt)
    let sampleData: string | null = null;
    const dataFiles = ['data.csv', 'sales.txt'];
    for (const dataFile of dataFiles) {
      const dataPath = path.join(questionDir, dataFile);
      if (fs.existsSync(dataPath)) {
        sampleData = fs.readFileSync(dataPath, 'utf-8');
        break;
      }
    }

    const slug = slugify(title);

    await prisma.moduleQuestion.upsert({
      where: { uq_mq_module_slug: { module_id: moduleId, slug } },
      update: {
        module_id: moduleId,
        slug,
        folder_name: folderName,
        title,
        difficulty,
        topic,
        tags,
        question_py: questionPy,
        initial_code: initialCode,
        validator_py: validatorPy,
        hint,
        sample_data: sampleData,
        is_verified: true,
        is_active: active,
      },
      create: {
        module_id: moduleId,
        slug,
        folder_name: folderName,
        title,
        difficulty,
        topic,
        tags,
        question_py: questionPy,
        initial_code: initialCode,
        validator_py: validatorPy,
        hint,
        sample_data: sampleData,
        is_verified: true,
        is_active: active,
      },
    });

    console.log(
      `  ✓ [module:${moduleKey}#${moduleId}] ${legacyQuestionId || slug} — "${title}" (${difficulty})`,
    );
    seeded++;
  }

  console.log(`\nSeeded ${seeded} question(s), skipped ${skipped}`);
}

// ─── Main ────────────────────────────────────────────────────────────────────

async function main() {
  console.log('Starting database seed...\n');
  await seedModules();
  await seedQuestions();
  console.log('\nSeed completed.');
}

main()
  .catch((e) => {
    console.error('Seed error:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
