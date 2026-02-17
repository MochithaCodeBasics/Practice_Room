import * as path from 'path';

export default () => ({
  port: parseInt(process.env.PORT ?? '3001', 10),
  environment: process.env.ENVIRONMENT || 'development',
  database: {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT ?? '3306', 10),
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    name: process.env.DB_NAME || 'practice_room',
  },
  jwt: {
    secret: process.env.SECRET_KEY || 'dev-only-insecure-key-change-in-production',
    expirationMinutes:
      parseInt(process.env.JWT_EXPIRATION_MINUTES ?? '1440', 10),
  },
  admin: {
    username: process.env.DEFAULT_ADMIN_USERNAME || 'admin',
    password: process.env.DEFAULT_ADMIN_PASSWORD || '',
    email: process.env.DEFAULT_ADMIN_EMAIL || 'admin@example.com',
    emails: (process.env.ADMIN_EMAILS || process.env.DEFAULT_ADMIN_EMAIL || 'admin@example.com')
      .split(',')
      .map((s) => s.trim().toLowerCase())
      .filter(Boolean),
  },
  docker: {
    useDocker: process.env.USE_DOCKER_EXECUTOR !== 'false',
    timeout: parseInt(process.env.DOCKER_TIMEOUT ?? '30', 10),
    memoryLimit: process.env.DOCKER_MEMORY_LIMIT || '128m',
    cpuLimit: parseFloat(process.env.DOCKER_CPU_LIMIT ?? '0.5'),
  },
  cors: {
    origins: (
      process.env.CORS_ORIGINS ||
      'http://localhost:5173,http://localhost:3000,http://localhost:3002'
    )
      .split(',')
      .map((s) => s.trim()),
  },
  questionsDir:
    process.env.QUESTIONS_DIR
      ? path.resolve(process.env.QUESTIONS_DIR)
      : path.resolve(__dirname, '..', '..', '..', 'questions'),
  smtp: {
    host: process.env.SMTP_HOST || 'smtp.gmail.com',
    port: parseInt(process.env.SMTP_PORT ?? '587', 10),
    user: process.env.SMTP_USER || '',
    password: process.env.SMTP_PASSWORD || '',
    fromEmail:
      process.env.SMTP_FROM_EMAIL || process.env.SMTP_USER || '',
  },
  judge0: {
    apiUrl: process.env.JUDGE0_API_URL || 'http://localhost:2358',
    apiKey: process.env.JUDGE0_API_KEY || undefined,
    enabled: process.env.USE_JUDGE0 === 'true',
  },
  frontendUrl: process.env.FRONTEND_URL || 'http://localhost:3000',
});
