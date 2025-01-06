async def initial_job(*args):
    from scraper import Scraper
    scraper: Scraper = args[0]
    from sqlalchemy.orm import Session
    db_session: Session = args[1]

    from models import Team, Match, TeamStat, PlayerStat

    print("Checking teams in the db")
    tc = db_session.query(Team).count()
    if tc != 20:
        print("No teams in the db, fetching from the api")
        if tc != 0:
            db_session.query(Team).delete()

        teams = await scraper.fetch_teams()
        if len(teams) != 20:
            print("Not all teams were fetched, exiting")
            return

        for t in teams:
            t.stadium = await scraper.fetch_team_stadium(t)

        db_session.add_all(teams)
        db_session.commit()
        team_n = db_session.query(Team).count()
        print(f"{team_n} Teams was successfully fetched")

    print("Checking matches in the db")
    if db_session.query(Match).count() == 0:
        print("No matches in the db, fetching from the api")
        teams = db_session.query(Team).all()
        played_matches = await scraper.fetch_matches(teams, next_matches=False)
        future_matches = await scraper.fetch_matches(teams, next_matches=True)
        db_session.add_all(played_matches)
        db_session.add_all(future_matches)
        db_session.commit()
        finished_n = db_session.query(Match).filter_by(is_finished=True).count()
        future_n = db_session.query(Match).filter_by(is_finished=False).count()
        print(
            f"{finished_n+future_n} Matches ( played={finished_n}, next={future_n}) was successfully fetched"
        )

    print("Checking stats of match in the db")
    if db_session.query(TeamStat).count() == 0:
        print("No stats in the db, fetching from the api")
        matches = db_session.query(Match).filter_by(is_finished=True).all()
        with db_session.no_autoflush:
            for i in range(len(matches)):
                matches[i] = await scraper.fetch_match(matches[i])

        db_session.flush(matches)
        db_session.commit()
        match_n = db_session.query(TeamStat).count()
        player_n = db_session.query(PlayerStat).count()
        print(f"{match_n} Match Stats was successfully fetched")
        print(f"{player_n} Player Stats was successfully fetched")

    await handle_players(scraper, db_session)
    print("Initial job done")

async def handle_players(*args):
    from scraper import Scraper
    scraper: Scraper = args[0]

    from sqlalchemy.orm import Session
    db_session: Session = args[1]

    from models import PlayerStat, Player, Team

    print("Checking players in the db")
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
