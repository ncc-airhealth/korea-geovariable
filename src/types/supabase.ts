
export interface ApiTestResult {
  id: string;
  user_id: string;
  endpoint: string;
  border_type: string;
  year: number;
  task_id: string;
  status: string | null;
  result: any | null;
  created_at: string;
}

export type BorderType = 'sgg' | 'emd' | 'jgg';

export interface Profile {
  id: string;
  username: string | null;
  created_at: string;
}

export interface ApiEndpoint {
  name: string;
  path: string;
  description: string;
  category: string;
}
