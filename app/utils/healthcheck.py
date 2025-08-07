import httpx
import time

async def check_service(url: str):
    try:
        start = time.time()
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
        response_time = (time.time() - start) * 1000
        status = "UP" if response.status_code == 200 else "DOWN"
        return status, response_time
    except Exception:
        return "DOWN", None