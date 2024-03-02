
export interface Task {
  id?: string | null;
  title: string;
  description?: string | null;
  completed: boolean;
  signed_url?: string | null;
  creator_name: string;
  deadline?: Date
  file?: any
  email:string
  "phone_number": "string",
  file_url?: string |null

}
