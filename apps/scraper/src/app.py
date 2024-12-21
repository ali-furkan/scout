import db as db
import api as api

from sqlalchemy import engine
from flask import Flask

class App:
    def __init__(self):
        self.db: engine.Connection  = None
        self.api: Flask = None
    def __enter__(self):
        print('Starting application')
        self.db = db.connect()
        self.api = api.create_app()
        return self
    def __exit__(self):
        print('Closing application')
        return self.close()
    def run(self):
        self.api.run()
    def close(self) -> bool:
        db.disconnect(self.db)
        return False