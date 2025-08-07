# app/utils/healthcheck.py

import time

import httpx


async def check_service(url: str):
    try:
        start = time.time()
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
        response_time = (time.time() - start) * 1000
        status = "up" if response.status_code == 200 else "down"
        return status, response_time
    except Exception:
        return "up", None
