# InferHub

A production-style backend system that exposes unified REST APIs to serve multiple Large Language Models (LLMs). The system routes requests to different models, supports concurrent inference using FastAPI, caches responses with Redis, and logs observability metrics to PostgreSQL.

## Features

- **API Gateway**: Asynchronous FastAPI server exposing REST APIs for model inference.
- **Model Router**: Dispatches requests dynamically based on the requested model name.
- **Model Workers**: Pluggable architecture supporting OpenAI (`gpt4`, `gpt-3.5-turbo`) and local HuggingFace dummy models (`llama3`).
- **Caching Layer**: Leverages Redis structure to cache prompt-response pairs and avoid unnecessary external API costs or latency.
- **Database Logging**: Asynchronously logs inference metrics (timestamp, latency, token lengths) to PostgreSQL using SQLAlchemy and `asyncpg`.
- **Observability**: Prometheus metrics are available at `/metrics` tracking request latency, request count globally, and cache hit/miss rates.

## Architecture
* FastAPI routes the incoming request to the Model Router.
* Before generating, it queries the Redis Cache.
* If a cache miss occurs, the Model Router dispatches the request to the correct worker (OpenAI or HF).
* Result is cached in Redis.
* Inference stats are dumped asynchronously into Postgres via `BackgroundTasks`.

## Project Structure

```
InferHub/
├── api/
│   ├── main.py        - FastAPI App Entrypoint
│   └── routes.py      - HTTP Endpoint Handlers
├── cache/
│   └── redis_client.py- Async Redis abstraction wrapper
├── core/
│   ├── config.py      - Pydantic Settings
│   └── logger.py      - Structured Python Logging
├── database/
│   ├── db.py          - Async SQLAlchemy session and init logic
│   └── models.py      - DB Schemas (InferenceLogs)
├── metrics/
│   └── stats.py       - Prometheus metric definitions
├── router/
│   └── dispatcher.py  - Model Routing logic
├── workers/
│   ├── base.py        - Abstract Base Worker
│   ├── huggingface.py - HuggingFace Dummy implementation
│   └── openai.py      - Async OpenAI Client implementation
├── docker-compose.yml - Multi-container setup
├── Dockerfile         - Application image
└── requirements.txt
```

## Running the Project Locally

### 1. Configure the Environment

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Set your API keys inside `.env` if you want to test OpenAI integration limitlessly.
```env
OPENAI_API_KEY=your-openai-api-key
HF_API_TOKEN=your-token
```

### 2. Start Services via Docker Compose

```bash
docker-compose up --build
```

This starts:
- **gateway_api**: The FastAPI application on port 8000
- **db**: PostgreSQL database on port 5432
- **redis**: Redis Cache on port 6379

---

## API Usage Examples

### 1. Get Models
Returns a list of supported models.

```bash
curl -X GET http://localhost:8000/models
```
**Response:**
```json
{"models":["gpt4","gpt-3.5-turbo","llama3"]}
```

### 2. Generate Inference
Generates text using the requested model.

```bash
curl -X POST http://localhost:8000/v1/inference \
     -H "Content-Type: application/json" \
     -d '{
           "model": "llama3",
           "prompt": "Explain distributed systems in one sentence."
         }'
```

**Response (First attempt - Cache Miss):**
```json
{
  "response": "[Simulated Local llama3 Response] You requested: 'Explain distributed systems in one sentence.'",
  "cached": false
}
```

**Response (Second attempt - Cache Hit):**
```json
{
  "response": "[Simulated Local llama3 Response] You requested: 'Explain distributed systems in one sentence.'",
  "cached": true
}
```

### 3. Get Metrics
Scrape Prometheus metrics for observability.

```bash
curl -X GET http://localhost:8000/metrics | grep -E 'gateway_requests_total|gateway_cache'
```

**Output snippet:**
```text
# HELP gateway_requests_total Total number of inference requests
# TYPE gateway_requests_total counter
gateway_requests_total{model="llama3",status="success"} 2.0
# HELP gateway_cache_hits_total Total number of cache hits
# TYPE gateway_cache_hits_total counter
gateway_cache_hits_total{model="llama3"} 1.0
# HELP gateway_cache_misses_total Total number of cache misses
# TYPE gateway_cache_misses_total counter
gateway_cache_misses_total{model="llama3"} 1.0
```

### 4. Database Telemetry
Inference runs are correctly tracked in the PostgreSQL backend:

```text
 id |           timestamp           | model_used | prompt_length | response_length |     latency_ms     
----+-------------------------------+------------+---------------+-----------------+--------------------
  1 | 2026-03-16 05:56:13.509185+00 | llama3     |            44 |              95 | 2011.3394260406494
  2 | 2026-03-16 05:56:24.47726+00  | llama3     |            44 |              95 | 0.4062652587890625
```
