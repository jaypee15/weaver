from celery import Celery
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from app.config import settings


def _ensure_rediss_ssl_params(url: str) -> str:
  """
  Celery's Redis backend requires rediss:// URLs to specify ssl_cert_reqs.
  Upstash uses TLS with CA verification, so we set ssl_cert_reqs=required if missing.
  """
  if not url.startswith("rediss://"):
    return url

  parsed = urlparse(url)
  query = dict(parse_qsl(parsed.query))

  if "ssl_cert_reqs" not in query:
    # Use 'required' to validate server certs (recommended for Upstash)
    query["ssl_cert_reqs"] = "required"

  new_query = urlencode(query)
  return urlunparse(parsed._replace(query=new_query))


redis_url = _ensure_rediss_ssl_params(settings.REDIS_URL)

celery_app = Celery(
    "weaver",
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)

celery_app.autodiscover_tasks(["app.workers"])

