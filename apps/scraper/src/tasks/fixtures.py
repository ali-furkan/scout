import logging
import aiohttp
from scraper import ENDPOINT_MATCH_INFO

async def handle_fixture(*args):
    from scraper import Scraper
    scraper: Scraper = args[0]
    from sqlalchemy.orm import Session
    db_session: Session = args[1]

    match_id = args[2]

    from models import Match
    match = db_session.query(Match).filter_by(id=match_id).first()
    if match.is_finished:
        logging.warning(f"{match_id} match is already finished")
        return

    data_info = None
    async with aiohttp.ClientSession() as session:
        data_info = await scraper.fetch_api(session=session, endpoint=ENDPOINT_MATCH_INFO.format(match_id=match_id), cache=False)

    if data_info["event"]["status"]["type"] != "finished":
        logging.warning(f"{match_id} match is not finished")
        # NOTE: schedule the job to check the match again in 5 minutes
        # cancel tracking the match if the checking job is scheduled more than 5 times
        return

    logging.info(f"Match {match_id} is ended")
    match.is_finished = True

    match = await scraper.fetch_match(match)
    db_session.commit()
