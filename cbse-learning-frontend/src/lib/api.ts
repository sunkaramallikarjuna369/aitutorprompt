const RAW_API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Extract credentials from URL if present (for tunnel URLs with basic auth)
function parseApiUrl(url: string): { baseUrl: string; basicAuth: string | null } {
  try {
    const urlObj = new URL(url);
    if (urlObj.username && urlObj.password) {
      const basicAuth = btoa(`${urlObj.username}:${urlObj.password}`);
      urlObj.username = '';
      urlObj.password = '';
      return { baseUrl: urlObj.toString().replace(/\/$/, ''), basicAuth };
    }
    return { baseUrl: url, basicAuth: null };
  } catch {
    return { baseUrl: url, basicAuth: null };
  }
}

const { baseUrl: API_URL, basicAuth: BASIC_AUTH } = parseApiUrl(RAW_API_URL);

interface ApiOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
}

async function apiRequest<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
  const token = localStorage.getItem('token');
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  // Add Basic Auth header if tunnel credentials are present
  if (BASIC_AUTH) {
    headers['Authorization'] = `Basic ${BASIC_AUTH}`;
  }
  
  // JWT token takes precedence over Basic Auth for authenticated requests
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    method: options.method || 'GET',
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(error.detail || 'An error occurred');
  }
  
  return response.json();
}

export const authApi = {
  register: (data: { email: string; password: string; name: string; class_id?: string; student_mode?: StudentMode }) =>
    apiRequest<{ access_token: string; user: User }>('/auth/register', { method: 'POST', body: data }),
  
  login: (data: { email: string; password: string }) =>
    apiRequest<{ access_token: string; user: User }>('/auth/login', { method: 'POST', body: data }),
  
  getMe: () => apiRequest<User>('/auth/me'),
  
  updateProfile: (data: { name?: string; learning_style?: string; student_mode?: StudentMode; pace?: string }) =>
    apiRequest<User>('/auth/me', { method: 'PUT', body: data }),
};

export const curriculumApi = {
  getClasses: () => apiRequest<{ classes: ClassData[]; total: number }>('/curriculum/classes'),
  
  getClass: (classId: string) => apiRequest<ClassData>(`/curriculum/classes/${classId}`),
  
  getSubjectsByClass: (classId: string) =>
    apiRequest<{ subjects: Subject[]; total: number }>(`/curriculum/classes/${classId}/subjects`),
  
  getChaptersBySubject: (subjectId: string) =>
    apiRequest<{ chapters: Chapter[]; total: number }>(`/curriculum/subjects/${subjectId}/chapters`),
  
  getChapter: (chapterId: string) => apiRequest<ChapterWithTopics>(`/curriculum/chapters/${chapterId}`),
  
  getTopicsByChapter: (chapterId: string) =>
    apiRequest<{ topics: Topic[]; total: number }>(`/curriculum/chapters/${chapterId}/topics`),
  
  getHierarchy: () => apiRequest<{ hierarchy: ClassHierarchy[] }>('/curriculum/hierarchy'),
};

export const contentApi = {
  getTopicContent: (topicId: string) => apiRequest<TopicContent>(`/content/topics/${topicId}`),
  
  getVisualConfig: (topicId: string) =>
    apiRequest<{ topic_id: string; visual_configs: VisualConfig[] }>(`/content/topics/${topicId}/visual-config`),
  
  getSGTFlow: (chapterId: string) => apiRequest<SGTFlow>(`/content/chapters/${chapterId}/sgt-flow`),
};

export const visualizationApi = {
  analyzeQuadratic: (data: { a: number; b: number; c: number }) =>
    apiRequest<QuadraticAnalysis>('/visualization/quadratic/analyze', { method: 'POST', body: data }),
  
  getPlotPoints: (data: { a: number; b: number; c: number; x_min?: number; x_max?: number }) =>
    apiRequest<{ points: { x: number; y: number }[] }>('/visualization/quadratic/plot-points', { method: 'POST', body: data }),
  
  getSolutionSteps: (data: { a: number; b: number; c: number }) =>
    apiRequest<{ steps: SolutionStep[] }>('/visualization/quadratic/solve-steps', { method: 'POST', body: data }),
};

export const rwalApi = {
  getTopicRWAL: (topicId: string) => apiRequest<RWALResponse>(`/rwal/topics/${topicId}`),
  
  getPersonalizedExamples: (topicId: string, profile: StudentProfile) =>
    apiRequest<PersonalizedRWAL>(`/rwal/topics/${topicId}/personalized-examples`, { method: 'POST', body: { student_profile: profile } }),
  
  getSGTEntry: (chapterId: string) => apiRequest<SGTEntry>(`/rwal/chapters/${chapterId}/sgt-entry`),
};

export const quizApi = {
  startQuiz: (chapterId: string, data: { quiz_type?: string; question_count?: number }) =>
    apiRequest<QuizStart>(`/quiz/chapters/${chapterId}/start`, { method: 'POST', body: data }),
  
  submitAnswer: (sessionId: string, data: { question_id: string; answer: string; confidence_level?: number; response_time_ms: number }) =>
    apiRequest<AnswerResponse>(`/quiz/${sessionId}/answer`, { method: 'POST', body: data }),
  
  finishQuiz: (sessionId: string) =>
    apiRequest<QuizReport>(`/quiz/${sessionId}/finish`, { method: 'POST' }),
  
  getReport: (sessionId: string) => apiRequest<QuizReport>(`/quiz/${sessionId}/report`),
};

export const progressApi = {
  getMyProgress: () => apiRequest<ProgressSummary>('/progress/me/chapters'),
  
  getChapterProgress: (chapterId: string) => apiRequest<ChapterProgress>(`/progress/me/chapters/${chapterId}`),
  
  recordTopicViewed: (chapterId: string, data: { topic_id: string; time_spent_minutes: number; content_blocks_viewed: string[] }) =>
    apiRequest<TopicViewedResponse>(`/progress/me/chapters/${chapterId}/topic-viewed`, { method: 'POST', body: data }),
  
  getSummary: () => apiRequest<UserProgressSummary>('/progress/me/summary'),
};

export const recommendationApi = {
  getNextSteps: () => apiRequest<RecommendationsResponse>('/recommendations/me/next-steps'),
  
  getReviewPlan: () => apiRequest<ReviewPlan>('/recommendations/me/review-plan'),
  
  getLearningPath: () => apiRequest<LearningPath>('/recommendations/me/learning-path'),
};

export type StudentMode = 'dull' | 'average' | 'clever';

export const visualizationOrchestratorApi = {
  getModes: () => apiRequest<{ modes: StudentModeInfo[] }>('/visualization-orchestrator/modes'),
  
  getVisualConfig: (topicId: string, data: { student_mode?: StudentMode; mastery_level?: number }) =>
    apiRequest<VisualConfigResponse>(`/visualization-orchestrator/topics/${topicId}/config`, { method: 'POST', body: data }),
  
  previewConfigs: (topicId: string) =>
    apiRequest<{ topic_id: string; configs_by_mode: Record<StudentMode, AIVisualConfig> }>(`/visualization-orchestrator/topics/${topicId}/config/preview`),
  
  getWorkedExample: (topicId: string, data: { problem: string; student_mode?: StudentMode }) =>
    apiRequest<WorkedExampleResponse>(`/visualization-orchestrator/topics/${topicId}/worked-example`, { method: 'POST', body: data }),
  
  getPromptTemplates: () => apiRequest<PromptTemplatesResponse>('/visualization-orchestrator/prompt-templates'),
};

export interface StudentModeInfo {
  id: StudentMode;
  name: string;
  description: string;
  features: string[];
  recommended_for: string;
}

export interface AIVisualConfig {
  topic_id: string;
  student_mode: StudentMode;
  visualization_type: string;
  title: string;
  description: string;
  animation: {
    speed: number;
    easing: string;
    duration_ms: number;
    auto_play: boolean;
    loop: boolean;
  };
  x_axis: AxisConfig;
  y_axis: AxisConfig;
  colors: ColorScheme;
  scaffolding: ScaffoldingConfig;
  interactivity: InteractivityConfig;
  advanced: AdvancedFeatures;
  initial_values: Record<string, number>;
  value_ranges: Record<string, { min: number; max: number; step: number }>;
  annotations: unknown[];
  pedagogical_notes: string[];
}

export interface AxisConfig {
  show: boolean;
  color: string;
  label_size: number;
  grid_lines: boolean;
  grid_color: string;
  emphasis: string;
}

export interface ColorScheme {
  primary: string;
  secondary: string;
  background: string;
  text: string;
  accent: string;
  error: string;
  success: string;
}

export interface ScaffoldingConfig {
  level: string;
  show_hints: boolean;
  show_step_numbers: boolean;
  highlight_key_points: boolean;
  use_metaphors: boolean;
  metaphor_type: string | null;
}

export interface InteractivityConfig {
  sandbox_mode: boolean;
  slider_controls: boolean;
  click_to_explore: boolean;
  drag_enabled: boolean;
  zoom_enabled: boolean;
  reset_button: boolean;
}

export interface AdvancedFeatures {
  show_discriminant: boolean;
  show_complex_roots: boolean;
  show_3d_transformation: boolean;
  show_derivative: boolean;
  show_integral: boolean;
  stress_test_mode: boolean;
}

export interface VisualConfigResponse {
  config: AIVisualConfig;
  prompt_template_used: string;
  ai_provider: string;
}

export interface WorkedExampleResponse {
  topic_id: string;
  student_mode: StudentMode;
  worked_example: {
    problem: string;
    steps: { step: number; action: string; explanation: string; visual_hint?: string }[];
    final_answer: string;
    real_world_connection?: string;
    verification?: string;
    advanced_analysis?: Record<string, string>;
  };
  ai_provider: string;
}

export interface PromptTemplatesResponse {
  description: string;
  templates: Record<StudentMode, { system_prompt: string; user_prompt_template: string }>;
  usage: Record<StudentMode, string>;
}

export interface User {
  id: string;
  email: string;
  name: string;
  class_id: string;
  school?: string;
  learning_style: string;
  student_mode: StudentMode;
  pace: string;
  role: string;
}

export interface ClassData {
  id: string;
  board: string;
  grade: number;
  name: string;
  description: string;
  subjects: string[];
}

export interface Subject {
  id: string;
  class_id: string;
  name: string;
  code: string;
  description: string;
  chapters: string[];
  icon: string;
}

export interface Chapter {
  id: string;
  subject_id: string;
  name: string;
  number: number;
  description: string;
  difficulty: string;
  topics: string[];
  estimated_time_hours: number;
}

export interface ChapterWithTopics extends Chapter {
  topics_data: Topic[];
}

export interface Topic {
  id: string;
  chapter_id: string;
  name: string;
  description: string;
  order: number;
  learning_objectives: LearningObjective[];
  content_blocks: ContentBlock[];
  estimated_time_minutes: number;
  tags: string[];
}

export interface LearningObjective {
  id: string;
  description: string;
  bloom_level: string;
  keywords: string[];
}

export interface ContentBlock {
  id: string;
  type: string;
  title: string;
  content: string;
  order: number;
  metadata: Record<string, unknown>;
  visual_config_ref?: string;
}

export interface TopicContent {
  topic: Topic;
  content_blocks: ContentBlock[];
  learning_objectives: LearningObjective[];
  visual_configs: VisualConfig[];
  rwal_scenarios: RWALScenario[];
  estimated_time_minutes: number;
}

export interface VisualConfig {
  id: string;
  type: string;
  title: string;
  description: string;
  config: Record<string, unknown>;
}

export interface RWALScenario {
  id: string;
  topic_id: string;
  title: string;
  description: string;
  category: string;
  daily_life_examples: string[];
  industry_use_cases: string[];
  career_links: string[];
  mini_project_ideas: string[];
}

export interface QuadraticAnalysis {
  a: number;
  b: number;
  c: number;
  discriminant: number;
  discriminant_interpretation: string;
  roots: number[] | null;
  roots_type: string;
  vertex: [number, number];
  axis_of_symmetry: number;
  direction: string;
  y_intercept: number;
  plot_points: [number, number][];
  equation_string: string;
  factored_form: string | null;
  vertex_form: string;
}

export interface SolutionStep {
  step: number;
  title: string;
  content: string;
}

export interface RWALResponse {
  topic_id: string;
  topic_name: string;
  scenarios: RWALScenario[];
  summary: {
    daily_life_examples: string[];
    industry_use_cases: string[];
    career_links: string[];
    mini_project_ideas: string[];
  };
}

export interface StudentProfile {
  learning_style?: string;
  difficulty_preference?: string;
  regional_context?: string;
  interests?: string[];
}

export interface PersonalizedRWAL {
  topic_id: string;
  student_id: string;
  personalized_scenarios: unknown[];
  profile_used: StudentProfile;
}

export interface SGTEntry {
  chapter_id: string;
  entry_topic: string | null;
  entry_content: ContentBlock | null;
  related_scenarios: RWALScenario[];
  hook_message: string;
}

export interface SGTFlow {
  chapter_id: string;
  chapter_name: string;
  entry_scenario: unknown;
  learning_stages: unknown[];
  total_topics: number;
  estimated_time_hours: number;
}

export interface QuizStart {
  session_id: string;
  chapter_id: string;
  quiz_type: string;
  total_questions: number;
  current_question: Question;
  current_index: number;
  time_limit_seconds: number;
}

export interface Question {
  id: string;
  question_text: string;
  type: string;
  bloom_level: string;
  difficulty: number;
  points: number;
  time_limit_seconds: number;
  hint?: string;
  options?: { id: string; text: string }[];
}

export interface AnswerResponse {
  is_correct: boolean;
  points_earned: number;
  correct_answer: string;
  explanation: string;
  current_score: number;
  questions_remaining: number;
  next_question?: Question;
  current_index?: number;
  time_limit_seconds?: number;
  quiz_completed?: boolean;
}

export interface QuizReport {
  session_id: string;
  chapter_id: string;
  total_questions: number;
  correct_answers: number;
  score_percentage: number;
  time_taken_seconds: number;
  bloom_breakdown: Record<string, { correct: number; total: number; percentage: number }>;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
}

export interface ProgressSummary {
  user_id: string;
  progress: ChapterProgressItem[];
  summary: {
    total_chapters_started: number;
    completed: number;
    in_progress: number;
    overall_completion_pct: number;
  };
}

export interface ChapterProgressItem {
  id: string;
  user_id: string;
  chapter_id: string;
  status: string;
  progress_pct: number;
  chapter_name: string;
  chapter_number: number;
}

export interface ChapterProgress {
  chapter_id: string;
  chapter_name: string;
  user_id: string;
  overall_progress: unknown;
  topics_progress: TopicProgressItem[];
  quiz_history: {
    scores: number[];
    average: number;
    attempts: number;
  };
  bloom_performance: Record<string, number>;
  strengths: string[];
  weaknesses: string[];
}

export interface TopicProgressItem {
  topic_id: string;
  topic_name: string;
  order: number;
  status: string;
  progress_pct: number;
  time_spent_minutes: number;
}

export interface TopicViewedResponse {
  message: string;
  topic_progress: unknown;
  chapter_progress_pct: number;
  chapter_status: string;
}

export interface UserProgressSummary {
  user_id: string;
  summary: {
    chapters_started: number;
    chapters_completed: number;
    total_time_spent_minutes: number;
    total_quizzes_taken: number;
    average_quiz_score: number;
  };
  learning_profile: {
    top_strengths: string[];
    areas_to_improve: string[];
    learning_style: string;
    pace: string;
  };
}

export interface RecommendationsResponse {
  user_id: string;
  recommendations: Recommendation[];
  generated_at: string;
}

export interface Recommendation {
  type: string;
  priority: number;
  chapter_id?: string;
  chapter_name?: string;
  topic_id?: string;
  topic_name?: string;
  reason: string;
  [key: string]: unknown;
}

export interface ReviewPlan {
  user_id: string;
  review_plan: {
    items_needing_review: unknown[];
    weak_areas_to_practice: unknown[];
    suggested_schedule: unknown[];
  };
  spaced_repetition_info: {
    method: string;
    intervals: string[];
  };
}

export interface LearningPath {
  user_id: string;
  class_id: string;
  class_name: string;
  learning_path: unknown[];
  overall_progress: {
    total_chapters: number;
    completed: number;
    in_progress: number;
  };
}

export interface ClassHierarchy extends ClassData {
  subjects_data: (Subject & { chapters_data: (Chapter & { topics_data: Topic[] })[] })[];
}
