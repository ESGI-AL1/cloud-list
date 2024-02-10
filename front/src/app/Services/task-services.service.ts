import { Injectable } from '@angular/core';

import {catchError, Observable, throwError} from "rxjs";
import {ValidationErrors} from "@angular/forms";
import {environment} from "../environments/environment";
import {Task} from "../Models/Task";
import {HttpClient, HttpClientModule} from "@angular/common/http";

@Injectable({
  providedIn: 'root',
})
export class TaskServicesService {
  API_URL = environment.apiUrl

  constructor(private http :HttpClient ) {

  }

  createTask(task: Task): Observable<Task> {
    return this.http.post<Task>(this.API_URL + '/tasks/', task)
  }

  createTaskFormData(taskData: FormData): Observable<Task> {
    return this.http.post<Task>(this.API_URL+ '/tasks/', taskData);
  }

  getAllTask(): Observable<Task[]> {
    return this.http.get<Task[]>(`${this.API_URL}/tasks/`).pipe(
      catchError(err => throwError(() => new Error(err)))
    );
  }

  deleteByTaskId(taskId: string): Observable<any> {
    return this.http.delete(`${this.API_URL}/tasks/${taskId}`)

  }

  updateTask(taskId: string, task: FormData): Observable<any> {
    return this.http.put(`${this.API_URL}/tasks/${taskId}`, task);
  }


}
