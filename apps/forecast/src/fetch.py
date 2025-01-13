import aiohttp

async def fetch(session: aiohttp.ClientSession, url: str):
    async with session.get(url) as response:
        return await response.json()
