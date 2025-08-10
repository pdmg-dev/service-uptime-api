# app/services/checker.py

import asyncio
import logging
import random
import ssl
from datetime import datetime, timezone
from typing import Optional, Tuple

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure HTTP client limits
_limits = httpx.Limits(max_connections=None, max_keepalive_connections=20)
client = httpx.AsyncClient(timeout=settings.http_timeout_seconds, limits=_limits)

# Concurrency control for service checks
semaphore = asyncio.Semaphore(settings.poll_concurrency)


async def _perform_request(
    url: str, retries: int = 3, base_delay: float = 0.5
) -> Tuple[Optional[int], Optional[float], Optional[str]]:
    """Performs an HTTP GET request with retry logic and exponential backoff."""
    attempt = 0
    while attempt < retries:
        start = asyncio.get_event_loop().time()
        try:
            response = await client.get(url)
            elapsed = (asyncio.get_event_loop().time() - start) * 1000
            return response.status_code, elapsed, response.text

        except (httpx.RequestError, httpx.TimeoutException, ssl.SSLError) as e:
            wait_time = base_delay * (2**attempt) + random.uniform(0, 0.3)
            print(
                f"[WARN] Attempt {attempt + 1}/{retries} for {url} failed: {e} → retrying in {wait_time:.2f}s"
            )
            await asyncio.sleep(wait_time)
            attempt += 1

    return None, None, None


async def check_service(
    url: str,
    retries: int = 3,
    delay: float = 0.5,
    keyword: str | None = None,
    slow_threshold_ms: float = 2000.0,
) -> Tuple[str, Optional[float]]:
    """Checks the health of a service by performing an HTTP request and analyzing the response."""
    async with semaphore:
        start_time = datetime.now(timezone.utc)
        logger.debug(f"[Start] Checking {url} at {start_time.isoformat()}")

        for attempt in range(1, retries + 1):
            try:
                code, response_time, response = await _perform_request(url)

                # Default status
                if code is None:
                    status = "DOWN"
                elif 200 <= code < 400:
                    status = "UP"
                    if response_time and response_time > slow_threshold_ms:
                        status = "SLOW"
                    if keyword and keyword not in (response or ""):
                        status = "INVALID_CONTENT"
                elif code == 429:
                    status = "LIMITED"
                elif code in (401, 403):
                    status = "FORBIDDEN"
                else:
                    status = "DOWN"

                if status != "UP":
                    logger.warning(f"Service {url} returned {code} → {status}")

                end_time = datetime.now(timezone.utc)
                logger.debug(
                    f"[End] {url} at {end_time.isoformat()} → {status} ({response_time:.2f} ms)"
                )
                return status, response_time

            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.RequestError) as e:
                logger.warning(f"Retryable error for {url} (attempt {attempt}): {e}")
                if attempt < retries:
                    await asyncio.sleep(delay * attempt)
                    continue
                return "UNREACHABLE", None

            except Exception as e:
                logger.exception(f"Unhandled error for {url}: {e}")
                return "DOWN", None
