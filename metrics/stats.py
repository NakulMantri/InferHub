from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

REQUEST_COUNT = Counter(
    "gateway_requests_total",
    "Total number of inference requests",
    ["model", "status"]
)

REQUEST_LATENCY = Histogram(
    "gateway_request_latency_seconds",
    "Request latency in seconds",
    ["model"]
)

CACHE_HITS = Counter(
    "gateway_cache_hits_total",
    "Total number of cache hits",
    ["model"]
)

CACHE_MISSES = Counter(
    "gateway_cache_misses_total",
    "Total number of cache misses",
    ["model"]
)

def get_metrics_response() -> Response:
    """Returns the current Prometheus metrics formatted for scraping."""
    metrics_data = generate_latest()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)
