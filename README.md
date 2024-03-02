# Cloud-list

Cloud-list is a simple to-do list using various cloud services

## Cloud services

This project uses various cloud services, you can check how and why we use these tools in the application.

- Google Cloud Platform - GCP
    - Cloud SQL: We store basic informations in a SQL database for a task in the todo-list, like the title, who created the task, a phone number where we can send notifcations etc.
    - Cloud Storage: A task can have a file attached to it, for this purpose we used a Bucket in the cloud. The path of the file is stored in the SQL database.
    - App Engine: The application is automatically deployed in the cloud using the App Engine service.
 
- Amazon Web Service - AWS
    - AWS API Gateway: When a new task is created, an endpoint is available to accept POST request. This endpoint will then launch a Lambda function.
    - AWS Lambda: If the endpoint has been triggerd, a AWS Lamba function is triggered to send a mobile notification to alert that a new task as been created.
    - AWS SNS: This service is used to handle mobile phone notifications when a new task is created if a phone number has been provided.
 
  
