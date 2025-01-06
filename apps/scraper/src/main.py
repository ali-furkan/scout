from app import App
import asyncio

async def main():
    with App() as a:
        from tasks import initial_job
        await initial_job(a.scraper, a.db_session)

        a.run()

if __name__ == "__main__":
    asyncio.run(main())
