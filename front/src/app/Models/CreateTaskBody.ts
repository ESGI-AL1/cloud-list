

export interface BodyCreateTask {
  title: string;
  description: string;
  completed: boolean;
  creator_name: string;
  deadline?: string | null;
  file: Blob;
}
