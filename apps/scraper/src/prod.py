from app import App
from flask import Flask


def run_app() -> App:
    a = App()
    a.__enter__()
    a.run()

    return a


def on_quit(signum, frame):
    if prod_app:
        prod_app.close()


prod_app: App = None
flask_app: Flask = None
from config import Config

if Config.get_env() == "production":
    prod_app = run_app()
    flask_app = prod_app.api
    import signal

    signal.signal(signal.SIGQUIT, on_quit)
