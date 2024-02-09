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

  createTask(task: Task): Observable<Task | ValidationErrors> {
    return this.http.post<Task>(this.API_URL + '/task/', task).pipe(
      catchError(err => throwError(() => new Error(err)))
    );
  }

  getAllTask(): Observable<Task[]> {
    return this.http.get<Task[]>(`${this.API_URL}/tasks/`).pipe(
      catchError(err => throwError(() => new Error(err)))
    );
  }

  deleteByTaskId(taskId: string): Observable<any> {
    return this.http.delete(`${this.API_URL}/tasks/${taskId}`).pipe(
      catchError(err => throwError(() => new Error(err)))
    );
  }

  updateByTaskId(taskId: string, task: Task): Observable<Task> {
    return this.http.put<Task>(`${this.API_URL}/tasks/${taskId}`, task).pipe(
      catchError(err => throwError(() => new Error(err)))
    );
  }
}
