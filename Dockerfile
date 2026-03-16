FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose FastAPI port
EXPOSE 8000
# Expose Prometheus metrics port if needed, but we'll use same port
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
