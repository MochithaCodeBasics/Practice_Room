export interface Module {
  id: string;
  name: string;
  slug: string;
  description?: string;
  is_active?: boolean;
  created_at?: string;
}

export interface QuestionRead {
  id: string;
  slug: string;
  title: string;
  folder_name: string;
  module_id: string;
  difficulty: string;
  topic?: string;
  tags?: string;
  is_verified?: boolean;
  is_completed: boolean;
  is_attempted: boolean;
}

export interface QuestionDetail extends QuestionRead {
  question_py: string;
  initial_code: string;
  validator_py: string;
  data_files: string[];
  hint?: string;
  sample_data?: string;
}

export interface ExecutionResult {
  stdout: string;
  stderr: string;
  artifacts?: string[];
  status: string;
  run_id?: string;
  current_streak?: number;
}

export interface User {
  id?: number;
  username: string;
  role: string;
  current_streak: number;
  has_groq_api_key?: boolean;
  has_openai_api_key?: boolean;
  has_anthropic_api_key?: boolean;
  default_llm_provider?: string;
  groq_api_key?: string;
  openai_api_key?: string;
  anthropic_api_key?: string;
}

export interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  adminLogin: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  signup: (username: string, email: string, password: string) => Promise<boolean>;
  refreshUser: () => Promise<void>;
  requestPasswordReset: (email: string) => Promise<boolean>;
  verifyPasswordReset: (token: string, newPassword: string) => Promise<boolean>;
}

export interface Filters {
  difficulty: string;
  status: string;
  topic: string;
}
