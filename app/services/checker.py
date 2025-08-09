# app/services/checker.py

import asyncio
import logging
import time
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

# Shared async client and semaphore
client = httpx.AsyncClient(timeout=5.0)
semaphore = asyncio.Semaphore(10)


async def check_service(
    url: str,
    retries: int = 3,
    delay: float = 0.5,
    keyword: str | None = None,
    slow_threshold_ms: float = 2000.0,
):
    async with semaphore:
        start_time = datetime.now(timezone.utc)
        logger.info(f"[Start] Checking {url} at {start_time.isoformat()}")

        for attempt in range(1, retries + 1):
            try:
                start = time.perf_counter()
                response = await client.get(url)
                response_time = (time.perf_counter() - start) * 1000

                # Classify status
                status = "DOWN"
                code = response.status_code

                if 200 <= code < 400:
                    status = "UP"
                    if response_time > slow_threshold_ms:
                        status = "SLOW"
                    if keyword and keyword not in response.text:
                        status = "INVALID_CONTENT"
                elif code == 429:
                    status = "LIMITED"
                elif code in (401, 403):
                    status = "FORBIDDEN"

                if status != "UP":
                    logger.warning(f"Service {url} returned {code} → {status}")

                end_time = datetime.now(timezone.utc)
                logger.info(
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
                logger.error(f"Unhandled error for {url}: {e}")
                return "DOWN", None
