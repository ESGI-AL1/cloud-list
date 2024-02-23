import os
import uuid
import requests
from google.cloud import storage
from urllib.parse import urlparse, unquote

bucket_name = os.environ.get("CLOUD_STORAGE_BUCKET_NAME")
lambda_endpoint = os.environ.get("AWS_LAMBDA_ENDPOINT")


def upload_file_cloud_storage(file):
    task_id = str(uuid.uuid4())
    file_name = f"{task_id}_{file.filename}"

    client = storage.Client()
    bucket = client.bucket(bucket_name=bucket_name)

    blob = bucket.blob(file_name)
    blob.upload_from_string(file.file.read(), content_type=file.content_type)

    return f"https://storage.googleapis.com/{bucket_name}/{file_name}"


def delete_file_from_cloud_storage(file_url):
    parsed_url = urlparse(unquote(file_url))
    path_parts = parsed_url.path.lstrip('/').split('/')
    filename = '/'.join(path_parts[1:])

    client = storage.Client()

    bucket = client.bucket(bucket_name)

    blob = bucket.blob(filename)

    blob.delete()

    return f"File {filename} deleted from bucket {bucket_name}."


def trigger_lambda_aws(phone_number, title):
    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'phoneNumber': phone_number,
        'message': 'A new task has been assigned to you: ' + title
    }

    response = requests.post(lambda_endpoint, json=data, headers=headers)

    if response.status_code == 200:
        print("Successfully notified about the new task.")
    else:
        print(f"Failed to send notification. Status code: {response.status_code}, Message: {response.text}")
