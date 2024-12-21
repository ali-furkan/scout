import os

def get_db_url() -> str:
    return os.getenv("PG_URI","postgresql://scraper:scraper@db:5432/scraper")

def get_base_api() -> str:
    return os.getenv("SCRAPER_BASE_API")