import db as db
import api as api
from sqlalchemy.orm import Session
from sqlalchemy import engine
from flask import Flask
from models import Base
from apscheduler.schedulers.background import BackgroundScheduler
from scraper import Scraper, ScraperConfig

import logging

class App:
    def __init__(self):
        self.db_engine: engine.Engine = None
        self.db_session: Session = None
        self.api: Flask = None
        self.scheduler: BackgroundScheduler # = create_scheduler()
        self.scraper: Scraper = None

    def __enter__(self):
        print('Starting application')
        logging.basicConfig(level=logging.DEBUG)
        # Database
        self.db_engine = db.create_db_engine()
        self.db_session = db.create_session(self.db_engine)
        Base.metadata.create_all(self.db_engine)

        self.api = api.create_app(self.db_session)

        self.scraper = Scraper(cfg=ScraperConfig.from_env())

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print('Closing application', exc_type, exc_value, traceback)
        return self.close()

    def run(self):
        # if not self.scheduler.running:
        #     print('Starting scheduler')
        #     self.scheduler.start()

        # init_jobs(self.scheduler, self.scraper, self.db_session)
        # self.scheduler.print_jobs()

        from config import Config
        if Config.get_env() == 'development':
            self.api.run(host=Config.get_host(), port=Config.get_port(), debug=True)

    def close(self) -> bool:
        # if self.scheduler.running:
        #     self.scheduler.shutdown()
        db.disconnect(self.db_session)
        self.scraper.close()
        return False
