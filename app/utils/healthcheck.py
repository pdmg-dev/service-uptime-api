# app/utils/healthcheck.py

import asyncio
import time

import httpx


async def check_service(url: str, retries: int = 3, delay: float = 0.5):
    for attempt in range(1, retries + 1):
        try:
            start = time.time()
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
            response_time = (time.time() - start) * 1000
            status = "up" if response.status_code == 200 else "down"
            return status, response_time
        except Exception:
            if attempt < retries:
                await asyncio.sleep(delay * attempt)
            else:
                return "down", None
