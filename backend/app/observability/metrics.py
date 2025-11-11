from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
from fastapi import FastAPI

query_counter = Counter(
    "weaver_queries_total",
    "Total number of queries",
    ["tenant_id", "confidence"],
)

query_latency = Histogram(
    "weaver_query_latency_seconds",
    "Query latency in seconds",
    ["tenant_id"],
)

ingestion_counter = Counter(
    "weaver_ingestion_total",
    "Total number of ingestion jobs",
    ["tenant_id", "status"],
)

active_tenants = Gauge(
    "weaver_active_tenants",
    "Number of active tenants",
)

api_errors = Counter(
    "weaver_api_errors_total",
    "Total API errors",
    ["endpoint", "status_code"],
)


def setup_metrics(app: FastAPI):
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

