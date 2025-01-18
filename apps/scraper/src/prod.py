from app import App
import asyncio
from flask import Flask


def run_app() -> App:
    a = App()
    a.__enter__()
    a.run()

    return a


def on_quit(signum, frame):
    if prod_app:
        prod_app.close()


prod_app: App = run_app()
flask_app: Flask = prod_app.api
async def run_jobs():
    from tasks import initial_job
    await initial_job(prod_app.scraper, prod_app.db_session)

asyncio.run(run_jobs())


import signal

signal.signal(signal.SIGQUIT, on_quit)
