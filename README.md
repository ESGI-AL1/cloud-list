# Cloud-list

Cloud-list is a simple to-do list using various cloud services

## Backend

The api is build with Python using FastAPI  
To start the api run the following commands:

    - `cd api && docker build -t cloudlist-api .`
    - `docker build -t cloudlist-api .`
    - `docker run -p 8000:80 cloudlist-api`

A swagger will be available @ `http://localhost:8000/docs` after building and running the api
