import os
import uuid
import requests
from google.cloud import storage
from urllib.parse import urlparse, unquote
import logging
from datetime import datetime, timedelta
from google.oauth2 import service_account

bucket_name = os.environ.get("CLOUD_STORAGE_BUCKET_NAME")
lambda_endpoint = os.environ.get("AWS_LAMBDA_ENDPOINT")
service_account_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")


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
    path_parts = parsed_url.path.lstrip("/").split("/")
    filename = "/".join(path_parts[1:])

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    blob = bucket.blob(filename)
    blob.delete()

    return f"File {filename} deleted from bucket {bucket_name}."


def trigger_lambda_aws(phone_number, title):
    headers = {"Content-Type": "application/json"}

    data = {
        "phoneNumber": phone_number,
        "message": "A new task has been assigned to you: " + title,
    }

    response = requests.post(lambda_endpoint, json=data, headers=headers)

    if response.status_code == 200:
        print("Successfully notified about the new task.")
    else:
        print(
            f"Failed to send notification: {response.status_code}, Message: {response.text}"
        )


def sign_url(file_url, expires_after_seconds=3600):
    try:
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file
        )
        client = storage.Client(credentials=credentials, project=credentials.project_id)

        parsed_url = urlparse(unquote(file_url))
        if (
            parsed_url.scheme != "https"
            or parsed_url.netloc != "storage.googleapis.com"
        ):
            raise Exception("Invalid URL")

        path_parts = parsed_url.path.lstrip("/").split("/", 1)
        if len(path_parts) != 2:
            raise Exception("Invalid URL path")
        _, file_name = path_parts

        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        if not blob.exists():
            raise Exception("File is not in the bucket")

        expiration_time = datetime.utcnow() + timedelta(seconds=expires_after_seconds)
        url = blob.generate_signed_url(expiration=expiration_time)

        return url

    except Exception as e:
        logging.error(f"Error: {e}")
        return None
