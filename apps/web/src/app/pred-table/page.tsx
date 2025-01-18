import { getStanding } from "@/utils/standing";
import { predictFixture } from "@/utils/predict";
import { fetchScraper } from "@/utils/fetch";
import Link from "next/link"

export default async function TablePage() {
    const results = await fetchScraper("/matches/results?limit=400").then((res) => res.json());
    let { matches }: { matches: any[] } = await fetchScraper("/matches/fixtures?limit=300").then((res) => res.json());
    const { teams }: { teams: any[] } = await fetchScraper("/teams").then((res) => res.json());
    const standing = getStanding(teams, results);
    
    const predictions = await Promise.all(matches.map(async (m)=>{
            const { fixture } = await predictFixture(m, standing);
    
            m["result"] = (fixture.home_win_prob - fixture.away_win_prob) > 0.1 ? 1 : (fixture.home_win_prob - fixture.away_win_prob) > -0.1 ? -1 : 0;

            return {
                ...m,
                home_team_: teams.find((t) => t.id === m.home_team),
                away_team_: teams.find((t) => t.id === m.away_team),
                analysis: fixture
            }
    }))

    const pteams = JSON.parse(JSON.stringify(teams));
    const standing2 = getStanding(pteams, { matches: predictions });
    console.log(standing2);

    const res = standing2.map((team: any) => {
        const originalTeam = standing.find((t: any) => t.id === team.id);
        console.log(originalTeam);

        return {
            ...team,
            played: team.played + (originalTeam ? originalTeam.played : 0),
            wins: team.wins + (originalTeam ? originalTeam.wins : 0),
            draws: team.draws + (originalTeam ? originalTeam.draws : 0),
            losses: team.losses + (originalTeam ? originalTeam.losses : 0),
            points: team.points + (originalTeam ? originalTeam.points : 0),
        };
    }).sort((a: any, b: any) => b.points - a.points).map((team: any, i) => ({
        ...team,
        position: i + 1
    }));

    console.log(res);

    

    return (
        <div className="mx-auto p-4 max-w-6xl">
            <h1 className="text-4xl font-bold">Tables</h1>
            <div className="flex flex-col ">
                <div className="flex justify-between items-center">
                    <h3 className="text-xl font-bold text-slate-800 dark:text-slate-500">Premier League Prediction Table</h3>
                    <Link href={"/tables"}>
                        <div className="flex items-center w-fit mt-4 justify-center dark:text-black text-white bg-black rounded-md px-4 py-1 dark:bg-white hover:opacity-80">
                            Go to Actual Table
                        </div>
                    </Link>
                </div>
                <div style={{ gridTemplateColumns: "3fr 1fr" }} className="grid gap-4 mt-5">
                    <span className="mr-4 font-bold text-left">Club</span>
                    <div className="flex gap-x-2">
                        <span className="font-bold">W</span>
                        <span className="font-bold">D</span>
                        <span className="font-bold">L</span>
                        <span className="flex-1 font-bold">P</span>
                    </div>
                    {res.map((team: any, i) => (
                        <> 
                            <div className="flex">

                                <span className="font-bold">{team.position}.</span>
                                <div className="w-5 h-5">
                                    <img src={`https://img.sofascore.com/api/v1/team/${team.sc_id}/image/small`} alt={team.name} />
                                </div>
                                <span>{team.name}</span>
                            </div>
                            <div className="flex gap-x-2">
                                <span>{team.wins}</span>
                                <span>{team.draws}</span>
                                <span>{team.losses}</span>
                                <span>{team.points}</span>
                            </div>
                        </>
                    ))}
                </div>
                    
            </div>
        </div>
    )
}