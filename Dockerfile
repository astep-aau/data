FROM python:3.14-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY import_data.py .
COPY bj_data.zip .

CMD ["python", "import_data.py"]
