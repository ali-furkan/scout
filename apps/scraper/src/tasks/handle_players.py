import logging

async def handle_players(*args):
    from scraper import Scraper

    scraper: Scraper = args[0]

    from sqlalchemy.orm import Session

    db_session: Session = args[1]

    from models import PlayerStat, Player, Team

    logging.info("Checking players in the db")
    players = db_session.query(Player).all()
    teams = db_session.query(Team).all()
    tid = list(map(lambda x: x.sc_id, teams))
    pid = list(map(lambda x: x.sc_id, players))
    stats = db_session.query(PlayerStat).all()
    with db_session.no_autoflush:
        for sp in stats:
            if sp.sc_id not in pid:
                player = await scraper.fetch_player(sp.sc_id)
                if player.team_sid in tid:
                    idx = tid.index(player.team_sid)
                    player.team_id = teams[idx].id
                db_session.add(player)
                db_session.commit()
                sp.player = player
                pid.append(sp.sc_id)
            elif sp.player_id is None:
                player = db_session.query(Player).filter_by(sc_id=sp.sc_id).first()
                sp.player_id = player.id

    db_session.flush(stats)

    db_session.commit()
