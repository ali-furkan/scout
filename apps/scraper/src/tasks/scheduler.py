from sqlalchemy import create_engine
from apscheduler.schedulers.background import BackgroundScheduler

def create_scheduler() -> BackgroundScheduler:
    from config import Config
    from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
    from apscheduler.executors.pool import ProcessPoolExecutor

    jobs_engine = create_engine(Config.get_jobs_db_url())
    jobstores = {
        'default': SQLAlchemyJobStore(engine=jobs_engine)
    }
    executors = {
        'default': {'type': 'threadpool', 'max_workers': 20},
        'processpool': ProcessPoolExecutor(max_workers=5)
    }

    return BackgroundScheduler(
        jobstores=jobstores,
        executors=executors,
        timezone='UTC'
    )

from scraper import Scraper
from sqlalchemy.orm import Session

def init_jobs(scheduler: BackgroundScheduler, scraper: Scraper, db_session: Session):
    from tasks import initial_job
    from datetime import datetime

    if not scheduler.get_job("initial_job"):
        scheduler.add_job(
            initial_job,
            trigger="date",
            run_date=datetime.now(),
            args=[scraper, db_session],
            id="initial_job",
        )