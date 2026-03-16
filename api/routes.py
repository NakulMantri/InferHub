import time
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from database.db import log_inference
from cache.redis_client import redis_client
from router.dispatcher import router as model_router
from metrics.stats import REQUEST_COUNT, REQUEST_LATENCY, CACHE_HITS, CACHE_MISSES, get_metrics_response
from core.logger import logger

api_router = APIRouter()

class InferenceRequest(BaseModel):
    model: str
    prompt: str

class InferenceResponse(BaseModel):
    response: str
    cached: bool = False

@api_router.post("/v1/inference", response_model=InferenceResponse)
async def inference(request: InferenceRequest, background_tasks: BackgroundTasks):
    start_time = time.time()
    model = request.model
    prompt = request.prompt
    
    # Check if model is supported
    if model not in model_router.get_supported_models():
        REQUEST_COUNT.labels(model=model, status="error").inc()
        raise HTTPException(status_code=400, detail=f"Unsupported model: {model}")
    
    # Check cache
    cached_resp = await redis_client.get_cached_response(model, prompt)
    if cached_resp:
        CACHE_HITS.labels(model=model).inc()
        REQUEST_COUNT.labels(model=model, status="success").inc()
        
        latency_ms = (time.time() - start_time) * 1000
        background_tasks.add_task(log_inference, model, len(prompt), len(cached_resp), latency_ms)
        REQUEST_LATENCY.labels(model=model).observe(time.time() - start_time)
        
        return InferenceResponse(response=cached_resp, cached=True)

    CACHE_MISSES.labels(model=model).inc()
    
    # Generate response
    try:
        response_text = await model_router.dispatch(model, prompt)
        
        # Save cache
        await redis_client.set_cached_response(model, prompt, response_text)
        
        # Log to DB
        latency_ms = (time.time() - start_time) * 1000
        background_tasks.add_task(log_inference, model, len(prompt), len(response_text), latency_ms)
        
        REQUEST_COUNT.labels(model=model, status="success").inc()
        REQUEST_LATENCY.labels(model=model).observe(time.time() - start_time)
        
        return InferenceResponse(response=response_text, cached=False)
    except Exception as e:
        REQUEST_COUNT.labels(model=model, status="error").inc()
        logger.error(f"Inference failed: {e}")
        raise HTTPException(status_code=500, detail="Inference generation failed")

@api_router.get("/models")
async def get_models():
    return {"models": model_router.get_supported_models()}

@api_router.get("/metrics")
async def metrics():
    return get_metrics_response()
