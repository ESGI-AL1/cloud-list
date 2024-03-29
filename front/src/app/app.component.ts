import {Component, ElementRef, HostListener, OnInit, ViewChild} from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {
  AbstractControl,
  FormBuilder,
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators
} from "@angular/forms";
import {DatePipe, NgClass, NgForOf, NgIf} from "@angular/common";
import {TaskServicesService} from "./Services/task-services.service";
import {Task} from "./Models/Task";
import {finalize} from "rxjs";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, ReactiveFormsModule, FormsModule, NgIf, NgForOf, DatePipe, NgClass],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit{
  updateForm!: FormGroup;
  currentMenuIndex: number | null = null;
  showModalDelete: boolean = false;
  existingFileName: string = '';
  title = 'front';
  taskTitle: string = '';
  protected isToggleTaskForm: boolean = false;
  protected tasks: Task[] | undefined = undefined;
  protected tmpTask: Task[] | undefined = undefined;
  showModal = false;
  selectedTask: Task | null = null;
  public isToggleUpdateForm: boolean = false;
  isNotToggleForm: boolean = true;
  public toggleSpinner = true ;

  constructor(private formBuilder : FormBuilder , private taskService: TaskServicesService){}
  ngOnInit() {
    this.taskService.getAllTask().subscribe(result=>{
      this.tmpTask = result

      this.tasks = result
      if(this.tasks){
        this.toggleSpinner = false
      }
    })
  }


  activeTag: string = 'all';
  taskForm = new FormGroup({
    title: new FormControl('', Validators.required),
    description: new FormControl(''),
    creator_name: new FormControl('', Validators.required),
    deadline: new FormControl(''),
    file: new FormControl(null),
    email: new FormControl('', [Validators.required, Validators.email]),
    phone_number: new FormControl('', [Validators.required,this.frenchPhoneNumberValidator])
  })

  initializeForm(): void {
    this.updateForm = this.formBuilder.group({
      title: [''],
      description: [''],
      completed: [false],
      creator_name: [''],
      deadline: [''],
      file: [null],
      email:['',[Validators.required, Validators.email]],
      phone_number: new FormControl('', [Validators.required,this.frenchPhoneNumberValidator])

    });
  }

  loadTaskDetails(task: Task): void {
    this.updateForm.patchValue({
      email: task.email,
      title: task.title,
      description: task.description,
      completed: task.completed,
      creator_name: task.creator_name,
      phone_number: task.phone_number,
      deadline: task.deadline ? new Date(task.deadline).toISOString().substring(0, 10) : null,
    });
    if (task.file_url) {
      const fileName = task.file_url.split('/').pop();
      this.existingFileName = fileName ? fileName : 'Attached file';
    } else {
      this.existingFileName = '';
    }


  }

  updateTask(taskId: string | null | undefined): void {
    if(taskId){
      if (this.updateForm) {
        this.toggleSpinner=true
        const formData = new FormData();
        Object.keys(this.updateForm.value).forEach(key => {
          const control = this.updateForm.get(key);
          if (control) {
            let value = control.value;

            if (key === 'deadline' && value) {
              value = new Date(value).toISOString().split('T')[0];
            }

            if (key === 'file' && value) {
              formData.append(key, value, value.name);
            } else if (value !== null) {
              formData.append(key, value.toString());
            }
          }
        });

        this.taskService.updateTask(taskId, formData).subscribe({

          next: (response) => {console.log('Task updated successfully', response);
            this.isNotToggleForm= true
            this.isToggleTaskForm = false
            this.isToggleUpdateForm =false
            this.ngOnInit()
          },
          error: (error) => console.error('Error updating task', error)
        });
      }
    }

  }

  toggleTaskForm() {
    this.isNotToggleForm = false
    this.isToggleUpdateForm= false
    this.isToggleTaskForm = true
    this.taskForm.get("title")?.setValue(this.taskTitle)
  }


  cancel() {
    this.isToggleTaskForm = false
    this.isToggleUpdateForm= false
    this.isNotToggleForm = true

  }


  frenchPhoneNumberValidator(control: AbstractControl): { [key: string]: any } | null {
    const phoneNumberRegex = /^(?:(?:(?:\+|00)33[\s.-]{0,3}(?:\(0\)[\s.-]{0,3})?)|0)(?:[\s.-]{0,3}[1-9](?:(?:[\s.-]?\d){1,}){8})$/;

    if (!phoneNumberRegex.test(control.value)) {
      return { 'frenchPhoneNumber': { value: control.value } };
    }

    return null;
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
    formData.append('email', this.taskForm.get('email')?.value ?? '');
    formData.append('phone_number', this.taskForm.get('phone_number')?.value ?? '');

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
    this.toggleSpinner=true

    this.taskService.createTaskFormData(formData).pipe(
      finalize(() => {
        this.ngOnInit();
      })
    ).subscribe({
      next: (task) => {
        this.isNotToggleForm= true
        this.isToggleTaskForm = false
        this.isToggleTaskForm =false
      },
      error: (error) => console.error('There are error !', error),
    });
  }

  onFileSelected(event: any) {
    if(this.taskForm && this.isToggleTaskForm)
    if (event.target.files.length > 0) {
      const file = event.target.files[0];
      this.existingFileName = file ? file.name : '';

      this.taskForm.patchValue({ file: file });
    }
    if(this.updateForm && this.isToggleUpdateForm){
      if (event.target.files.length > 0) {
        const file = event.target.files[0];
        this.existingFileName = file ? file.name : '';
        this.updateForm.patchValue({ file: file });
      }
    }
  }

  setActiveTag(tag: string) {
    const completedTasks = this.tasks
    this.activeTag = tag;
    if(this.activeTag==="completed" && completedTasks){
      this.tasks= this.tasks?.filter(task=> task.completed)
    }else{
      this.tasks = this.tmpTask
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

  onCheckboxChange(event: any, task: Task) {
    const formData = new FormData();
    task.completed = !task.completed;
    formData.append('completed', JSON.stringify(task.completed));
    if (task && task.id) {
      this.taskService.updateTask(task.id.toString(), formData).subscribe({
        next: (result) => {
          console.log("Update result:", result);
        },
        error: (error) => {
          console.error("Error updating task:", error);
        }
      });
    }
  }

  deleteTask(task: Task) {
    this.currentMenuIndex = null;
    this.showModalDelete = true;
    this.selectedTask= task;
    this.isNotToggleForm = true;


  }

  showDetails(task: Task) {
    this.currentMenuIndex = null;
    this.selectedTask = task;
    this.showModal = true;
    this.isNotToggleForm = true

  }

  confirmDeleteSelectedTask(task: Task|null) {
    if(task && task.id){
      this.toggleSpinner = true
    this.taskService.deleteByTaskId(task.id).subscribe(res=>{
      if(res){
        this.showModalDelete = false
        this.ngOnInit()
      }
    })
    }

  }
  cancelTaskCreation() {
    this.taskForm.reset();
    this.isToggleTaskForm = false;
    this.isToggleUpdateForm= false;
    this.isNotToggleForm = true

  }

  editTask(task: Task) {
    this.currentMenuIndex = null;
    this.isToggleTaskForm = false;
    this.isToggleUpdateForm= true;
    this.isNotToggleForm = false
    this.selectedTask= task
    this.initializeForm()
    console.log("je suis dans le details task")
    console.log(task)
    this.loadTaskDetails(task)

  }

  cancelUpdate() {
    this.taskForm.reset();
    this.isToggleTaskForm = false;
    this.isToggleUpdateForm= false;
    this.isNotToggleForm = true
  }



  isSelectedTaskAnImage(): boolean {
    if (!this.selectedTask?.signed_url) {
      return false;
    } else {
      const imageExtensions = ['png', 'jpg', 'jpeg', 'gif'];
      const extension = this.selectedTask.signed_url.split('.').pop()?.toLowerCase() ?? "";
      return imageExtensions.includes(extension);
    }
  }


}
