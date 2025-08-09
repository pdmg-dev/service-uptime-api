# app/services/checker.py

import asyncio
import time
import logging

import httpx

logger = logging.getLogger(__name__)


async def check_service(url: str, retries: int = 3, delay: float = 0.5):
    for attempt in range(1, retries + 1):
        try:
            start = time.time()
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
            response_time = (time.time() - start) * 1000
            status = "UP" if response.status_code == 200 else "DOWN"
            if status == "DOWN":
                logger.warning(f"Service {url} returned status {response.status_code}")
            return status, response_time
        except httpx.ConnectTimeout:
            logger.warning(f"Timeout when connecting to {url}")
            return "DOWN", None
        except httpx.ReadTimeout:
            logger.warning(f"Read timeout for {url}")
            return "DOWN", None
        except httpx.RequestError as e:
            logger.error(f"Request error for {url}: {e}")
            return "DOWN", None
        except Exception:
            if attempt < retries:
                await asyncio.sleep(delay * attempt)
            else:
                return "DOWN", None
