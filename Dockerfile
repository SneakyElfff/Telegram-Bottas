FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# data/ directory for last_notified.json and the database
RUN mkdir -p /app/data

CMD ["python", "main.py"]