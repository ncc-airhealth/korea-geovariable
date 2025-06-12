
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

export interface PointTestResult {
  id: string;
  user_id: string;
  endpoint: string;
  calculator_type: string;
  buffer_size: number;
  year: number;
  task_id: string;
  status: string | null;
  result: any | null;
  progress: any | null;
  created_at: string;
}

export interface CoordinateFile {
  id: string;
  user_id: string;
  file_name: string;
  file_path: string;
  description: string | null;
  coordinate_system: string;
  total_points: number;
  created_at: string;
  updated_at: string;
}
