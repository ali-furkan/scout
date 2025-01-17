export function getStanding(teams: any[], results: { matches: any[] }) {
    return teams.map((team: any, i) => {
        const team_matches: any[] = results.matches.filter((match: any) => match.home_team === team.id || match.away_team === team.id);

        const wins = team_matches.reduce((acc, match) => {
            if (match.home_team === team.id && match.result > 0) return acc + 1;
            if (match.away_team === team.id && match.result < 0) return acc + 1;
            return acc;
        }, 0)
        const draws = team_matches.reduce((acc, match) => {
            if (match.result == 0) return acc + 1;
            return acc;
        }, 0)
        return {
            ...team,
            played: team_matches.length,
            wins,
            draws,
            losses: team_matches.length - wins - draws,
            points: wins * 3 + draws,
            position: i + 1
        };
    }).sort((a: any, b: any) => b.points - a.points);
}