FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY cloudlist-413718-b669d1373b29.json /app/cloudlist-413718-b669d1373b29.json

ENV GOOGLE_APPLICATION_CREDENTIALS="/app/cloudlist-413718-b669d1373b29.json"

RUN mkdir /app/files && chmod 777 /app/files

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
