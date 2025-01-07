import logging

async def initial_job(*args):
    from scraper import Scraper
    scraper: Scraper = args[0]
    from sqlalchemy.orm import Session
    db_session: Session = args[1]

    from models import Team, Match, TeamStat, PlayerStat

    logging.info("Checking teams in the db")
    tc = db_session.query(Team).count()
    if tc != 20:
        logging.debug("No teams in the db, fetching from the api")
        if tc != 0:
            db_session.query(Team).delete()

        teams = await scraper.fetch_teams()
        if len(teams) != 20:
            logging.warning("Not all teams were fetched, exiting")
            return

        for t in teams:
            await scraper.fetch_team_features(t)

        db_session.add_all(teams)
        db_session.commit()
        team_n = db_session.query(Team).count()
        logging.info(f"{team_n} Teams was successfully fetched")

    logging.info("Checking matches in the db")
    if db_session.query(Match).count() == 0:
        logging.debug("No matches in the db, fetching from the api")
        teams = db_session.query(Team).all()
        played_matches = await scraper.fetch_matches(teams, next_matches=False)
        future_matches = await scraper.fetch_matches(teams, next_matches=True)
        db_session.add_all(played_matches)
        db_session.add_all(future_matches)
        db_session.commit()
        finished_n = db_session.query(Match).filter_by(is_finished=True).count()
        future_n = db_session.query(Match).filter_by(is_finished=False).count()
        # NOTE(ADD FEAT):Schedule the job to check future matches when they are finished
        logging.debug(
            f"{finished_n+future_n} Matches ( played={finished_n}, next={future_n}) was successfully fetched"
        )

    logging.info("Checking stats of match in the db")
    if db_session.query(TeamStat).count() == 0:
        logging.debug("No stats in the db, fetching from the api")
        matches = db_session.query(Match).filter_by(is_finished=True).all()
        with db_session.no_autoflush:
            for i in range(len(matches)):
                matches[i] = await scraper.fetch_match(matches[i])

        db_session.flush(matches)
        db_session.commit()
        match_n = db_session.query(TeamStat).count()
        player_n = db_session.query(PlayerStat).count()
        logging.debug(f"{match_n} Match Stats was successfully fetched")
        logging.debug(f"{player_n} Player Stats was successfully fetched")

    from .handle_players import handle_players
    await handle_players(scraper, db_session)
    logging.info("Initial job done")
