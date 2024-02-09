import {Component, OnInit} from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {FormBuilder, FormGroup, FormsModule, ReactiveFormsModule} from "@angular/forms";
import {NgForOf, NgIf} from "@angular/common";
import {TaskServicesService} from "./Services/task-services.service";
import {Task} from "./Models/Task";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, ReactiveFormsModule, FormsModule, NgIf, NgForOf],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit{
  title = 'front';
  taskForm!: FormGroup
  taskTitle: string = '';
  protected isToggleTaskForm: boolean = false;
  protected tasks: Task[] | undefined = undefined;

  constructor(private formBuilder : FormBuilder , private taskService: TaskServicesService){

  }
  ngOnInit() {
    this.taskForm = this.formBuilder.group({
      title: [''],
      description: [''],
      completed: [false],
      creator_name: [''],
      deadline: [''],
      file: ['']
    });
    this.taskService.getAllTask().subscribe(result=>{
      this.tasks = result
    })


  }

  resetForm() {

  }

  toggleTaskForm() {
    this.isToggleTaskForm = true
    this.taskForm.get("title")?.setValue(this.taskTitle)
  }

  createTask() {
    this.isToggleTaskForm = false
  }

  cancel() {
    this.isToggleTaskForm = false
  }
}
