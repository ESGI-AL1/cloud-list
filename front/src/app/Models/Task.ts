
export interface Task {
  id: string | null;
  title: string;
  description?: string | null;
  completed: boolean;
  file_url?: string | null;
  creator_name: string;
}
