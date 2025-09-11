import asyncio
import logging
import random
import ssl
from datetime import datetime, timezone
from typing import Optional, Tuple

import httpx

from app.core.config import settings
from app.models.service import ServiceState

# Initialize the logger
logger = logging.getLogger(__name__)

# Set HTTP client connection limits to optimize keep-alive behavior
_limits = httpx.Limits(max_connections=None, max_keepalive_connections=20)

# Create a reusable async HTTP client with custom timeout and headers
client = httpx.AsyncClient(
    timeout=settings.http_timeout_seconds,
    limits=_limits,
    headers={"User-Agent": "Mozilla/5.0 (compatible; ServiceUptimeBot/1.0)"},
)

# Semaphore to limit concurrent service checks (prevents overload)
semaphore = asyncio.Semaphore(settings.poll_concurrency)


def classify_status(
    code: int,
    response_time: Optional[float],
    keyword: Optional[str],
    response: Optional[str],
    slow_threshold_ms: int,
) -> ServiceState:
    """Classifies the service status based on HTTP response code, content, and latency."""
    if code is None:
        return ServiceState.UNREACHABLE.value

    if 200 <= code < 300:
        # Check for keyword presence in response body
        if keyword and keyword not in (response or ""):
            return ServiceState.INVALID_CONTENT.value
        # Check if response time exceeds threshold
        if response_time and response_time > slow_threshold_ms:
            return ServiceState.SLOW.value
        return ServiceState.UP.value

    # Handle redirects, rate limits, and auth errors
    if 300 <= code < 400:
        return ServiceState.REDIRECT
    if code == 429:
        return ServiceState.LIMITED.value
    if code in (401, 403):
        return ServiceState.FORBIDDEN.value

    # Default fallback for other error codes
    return ServiceState.DOWN.value


async def _perform_request(
    url: str, retries: int = 3, base_delay: float = 0.5
) -> Tuple[Optional[int], Optional[float], Optional[str]]:
    """Performs an HTTP GET request with retry and exponential backoff."""
    attempt = 0
    last_elapsed = None

    while attempt < retries:
        start = asyncio.get_event_loop().time()
        try:
            response = await client.get(url)
            elapsed = (asyncio.get_event_loop().time() - start) * 1000
            return response.status_code, elapsed, response.text
        # Timeout-specific handling
        except httpx.TimeoutException:
            last_elapsed = (asyncio.get_event_loop().time() - start) * 1000
            logger.warning(
                f"[Timeout] Attempt {attempt + 1}/{retries} for {url} timed out after {last_elapsed:.2f} ms"
            )
        # General request errors and SSL issues
        except (httpx.RequestError, ssl.SSLError) as e:
            logger.warning(
                f"[RequestError] Attempt {attempt + 1}/{retries} for {url} failed: {type(e).__name__} → {e}"
            )
        # Catch-all for unexpected exceptions
        except Exception as e:
            logger.exception(
                f"[Unhandled] Attempt {attempt + 1}/{retries} for {url}: {e}"
            )

        # Apply exponential backoff with jitter
        delay = base_delay * (2**attempt) + random.uniform(0, 0.3)
        logger.debug(f"[Backoff] Retrying {url} in {delay:.2f}s")
        await asyncio.sleep(delay)
        attempt += 1

    # Final fallback if all retries fail
    return None, last_elapsed, None


async def check_service(
    url: str,
    retries: int = 3,
    delay: float = 0.5,
    keyword: str | None = None,
    slow_threshold_ms: float = 2000.0,
) -> Tuple[str, Optional[float]]:
    """Main entry point to check the health of a service."""
    async with semaphore:
        start_time = datetime.now(timezone.utc)
        logger.debug(f"[Start] Checking {url} at {start_time.isoformat()}")

        try:
            code, response_time, response = await _perform_request(
                url, retries, delay
            )
            status = classify_status(
                code, response_time, keyword, response, slow_threshold_ms
            )
            # Log specific warnings for content mismatch or non-OK status
            if status == "INVALID_CONTENT":
                logger.warning(
                    f"[ContentMismatch] {url} missing keyword '{keyword}'"
                )
            elif status != "UP":
                logger.warning(
                    f"Service {url} returned {code or 'N/A'} → {status}"
                )

            end_time = datetime.now(timezone.utc)
            rt_display = (
                f"{response_time:.2f}" if response_time is not None else "N/A"
            )
            logger.debug(
                f"[End] {url} at {end_time.isoformat()} → {status} ({rt_display} ms)"
            )
            return status, response_time

        # Catch and log fatal errors
        except Exception as e:
            logger.exception(f"[Fatal] {url}: {e}")
            return "DOWN", None
