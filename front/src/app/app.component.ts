import {Component, HostListener, OnInit} from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {FormBuilder, FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators} from "@angular/forms";
import {DatePipe, NgForOf, NgIf} from "@angular/common";
import {TaskServicesService} from "./Services/task-services.service";
import {Task} from "./Models/Task";
import {finalize} from "rxjs";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, ReactiveFormsModule, FormsModule, NgIf, NgForOf, DatePipe],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit{

  taskForm = new FormGroup({
    title: new FormControl('', Validators.required),
    description: new FormControl(''),
    completed: new FormControl(false),
    creator_name: new FormControl('', Validators.required),
    deadline: new FormControl(''),
    file: new FormControl(null)
  });
  title = 'front';
  // taskForm!: FormGroup
  taskTitle: string = '';
  protected isToggleTaskForm: boolean = false;
  protected tasks: Task[] | undefined = undefined;
  showModal = false;
  selectedTask: Task | null = null;

  constructor(private formBuilder : FormBuilder , private taskService: TaskServicesService){

  }
  ngOnInit() {
    this.taskService.getAllTask().subscribe(result=>{
      this.tasks = result
      console.log(result)
    })


  }

  resetForm() {

  }

  toggleTaskForm() {
    this.isToggleTaskForm = true
    this.taskForm.get("title")?.setValue(this.taskTitle)
  }



  cancel() {
    this.isToggleTaskForm = false
  }



  valid() {
    if (this.taskForm.invalid) {
      return;
    }

    const formData = new FormData();
    formData.append('title', this.taskForm.get('title')?.value ?? '');
    formData.append('description', this.taskForm.get('description')?.value ?? '');
    formData.append('completed', String(this.taskForm.get('completed')?.value ?? false));
    formData.append('creator_name', this.taskForm.get('creator_name')?.value ?? '');

    const deadline = this.taskForm.get('deadline')?.value
    if (deadline) {
      formData.append('deadline',deadline);
    }

    const file = this.taskForm.get('file')?.value;
    if (file) {
      formData.append('file', file);
    }

    const fileControl = this.taskForm.get('file');
    if (fileControl && fileControl.value) {
      formData.append('file', fileControl.value);
    }

    this.taskService.createTaskFormData(formData).pipe(
      finalize(() => {
        this.ngOnInit();
      })
    ).subscribe({
      next: (task) => console.log(task),
      error: (error) => console.error('There are error !', error),
    });
  }

  onFileSelected(event: any) {
    if (event.target.files.length > 0) {
      const file = event.target.files[0];
      this.taskForm.patchValue({ file: file });
    }
  }

  @HostListener('document:click', ['$event'])
  clickOutside(event: any) {
    if (!event.target.closest('.menu-button') && !event.target.closest('.menu-content')) {
      this.currentMenuIndex = null;
    }
  }

  toggleMenu(index: number, event: MouseEvent) {
    event.stopPropagation();
    this.currentMenuIndex = this.currentMenuIndex === index ? null : index;
  }



  currentMenuIndex: number | null = null;
  showModalDelete: boolean = false;



  onCheckboxChange(event: any, task: Task) {
    task.completed = event.target.checked;
  }


  deleteTask(task: Task) {
    this.currentMenuIndex = null;
    this.showModalDelete = true
    this.selectedTask= task

  }

  showDetails(task: Task) {
    this.currentMenuIndex = null;
    this.selectedTask = task;
    this.showModal = true;
  }

  confirmDeleteSelectedTask(task: Task|null) {
    if(task && task.id)
    this.taskService.deleteByTaskId(task.id).subscribe(res=>{
      if(res){
        this.ngOnInit()
        this.showModalDelete = false
      }
    })

  }



  cancelTaskCreation() {
    this.taskForm.reset();
    this.isToggleTaskForm = false;
    // this.selectedTaskId = null;
  }


  editTask(task: Task) {
    this.currentMenuIndex = null;
    this.isToggleTaskForm = true;
    this.selectedTask= task


    // this.taskForm.setValue({
    //   title: task.title,
    //   description: task.description || '',
    //   completed: task.completed,
    //   creator_name: task.creator_name,
    //   deadline: task.deadline ? task.deadline : '',
    //   file: null // Les champs de fichier ne peuvent pas être préremplis pour des raisons de sécurité
    // });

    // Stockez l'ID de la tâche sélectionnée pour l'utilisation lors de la soumission
    // this.selectedTaskId = task.id; // Assurez-vous d'avoir une propriété selectedTaskId dans votre composant
  }


  submitForm() {

  }
}
