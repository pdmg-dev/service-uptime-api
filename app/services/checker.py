from __future__ import annotations

import asyncio
import logging
import random
import ssl
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.models.service import ServiceState

logger = logging.getLogger(__name__)

# HTTP client with no redirect following so 3xx codes are captured
_limits = httpx.Limits(max_connections=None, max_keepalive_connections=20)
client = httpx.AsyncClient(
    timeout=settings.http_timeout_seconds,
    limits=_limits,
    headers={"User-Agent": "Mozilla/5.0 (compatible; ServiceUptimeBot/1.0)"},
    follow_redirects=False,  # <<< important
)

semaphore = asyncio.Semaphore(settings.poll_concurrency)


def classify_status(
    code: int | None,
    response_time: float | None,
    keyword: str | None,
    response: str | None,
    slow_threshold_ms: int,
) -> ServiceState:
    """Classify service status by HTTP code, body keyword, and latency."""
    if code is None:
        return ServiceState.UNREACHABLE

    if 200 <= code < 300:
        if keyword and keyword not in (response or ""):
            return ServiceState.INVALID_CONTENT
        if response_time and response_time > slow_threshold_ms:
            return ServiceState.SLOW
        return ServiceState.UP

    if 300 <= code < 400:
        return ServiceState.REDIRECT
    if code == 429:
        return ServiceState.LIMITED
    if code in (401, 403):
        return ServiceState.FORBIDDEN
    return ServiceState.DOWN


async def _perform_request(
    url: str, retries: int = 3, base_delay: float = 0.5
) -> tuple[int | None, float | None, str | None]:
    """GET with retries and exponential backoff."""
    attempt, last_elapsed = 0, None
    loop = asyncio.get_running_loop()

    while attempt < retries:
        start = loop.time()
        try:
            r = await client.get(url)  # follow_redirects disabled on client
            return r.status_code, (loop.time() - start) * 1000, r.text
        except httpx.TimeoutException:
            last_elapsed = (loop.time() - start) * 1000
            logger.warning(
                "[Timeout] %s attempt %d/%d after %.2f ms",
                url,
                attempt + 1,
                retries,
                last_elapsed,
            )
        except (httpx.RequestError, ssl.SSLError) as e:
            logger.warning(
                "[RequestError] %s attempt %d: %s", url, attempt + 1, e
            )
        except Exception:
            logger.exception("[Unhandled] %s attempt %d", url, attempt + 1)

        delay = base_delay * (2**attempt) + random.uniform(0, 0.3)
        logger.debug("[Backoff] %s retry in %.2fs", url, delay)
        await asyncio.sleep(delay)
        attempt += 1

    return None, last_elapsed, None


async def check_service(
    url: str,
    retries: int = 3,
    delay: float = 0.5,
    keyword: str | None = None,
    slow_threshold_ms: int = 2000,
) -> tuple[ServiceState, float | None]:
    """Check the health of a service and return its state and latency."""
    async with semaphore:
        start = datetime.now(timezone.utc)
        logger.debug("[Start] %s at %s", url, start.isoformat())

        try:
            code, elapsed, text = await _perform_request(url, retries, delay)
            status = classify_status(
                code, elapsed, keyword, text, slow_threshold_ms
            )

            if status is ServiceState.INVALID_CONTENT:
                logger.warning(
                    "[ContentMismatch] %s missing '%s'", url, keyword
                )
            elif status is not ServiceState.UP:
                logger.warning(
                    "[Status] %s returned %s → %s", url, code or "N/A", status
                )

            if elapsed:
                logger.debug("[End] %s → %s (%.2f ms)", url, status, elapsed)
            else:
                logger.debug("[End] %s → %s", url, status)

            return status, elapsed
        except Exception:
            logger.exception("[Fatal] %s", url)
            return ServiceState.DOWN, None
