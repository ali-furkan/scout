import os

class Config:
    @staticmethod
    def cache_enabled() -> bool:
        return os.getenv("SCRAPER_CACHE_ENABLED", "true") == "true"
    
    def cache_ttl() -> int:
        return int(os.getenv("SCRAPER_CACHE_TTL", 60))
    
    def cache_file() -> str:
        return os.getenv("SCRAPER_CACHE_FILE", "cache.json")

    @staticmethod
    def get_db_url() -> str:
        return os.getenv("SCRAPER_DB_URI", "postgresql://scraper:scraper@db:5432/scraper")

    @staticmethod
    def get_jobs_db_url() -> str:
        return os.getenv("SCRAPER_JOBS_DB_URI", "postgresql://scraper:scraper@db:5432/jobs")

    @staticmethod
    def get_league_id() -> str:
        return os.getenv("SCRAPER_LEAGUE_ID", 17)

    @staticmethod
    def get_season_id() -> str:
        return os.getenv("SCRAPER_SEASON_ID", 61627)

    @staticmethod
    def get_base_api() -> str:
        return os.getenv("SCRAPER_BASE_API")

    @staticmethod
    def get_port() -> int:
        return int(os.getenv("SCRAPER_PORT", 5000))

    @staticmethod
    def get_host() -> str:
        return os.getenv("SCRAPER_HOST", "0.0.0.0")

    @staticmethod
    def get_env() -> str:
        return os.getenv("SCRAPER_ENV", "development")
