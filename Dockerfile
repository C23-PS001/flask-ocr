FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8080
ENV PORT 8080

CMD exec gunicorn --bind :$PORT main:app --workers 1 --threads 1 --timeout 1600
