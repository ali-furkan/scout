import aiohttp
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

async def fetch(session: aiohttp.ClientSession, uri: str):
    async with session.get(API_BASE_URL + uri) as response:
        return await response.json()
