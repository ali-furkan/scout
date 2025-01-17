import { getStanding } from "@/utils/standing";
import { predictFixture } from "@/utils/predict";

interface Match {
    id: string;
    played_at: string;
    home_team: string;
    away_team: string;
    is_finished: boolean;
    result: number;
    [key: string]: any;
}

export default async function MatchPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = await params;
    console.log(id);

    let { match } = await fetch(`http://localhost:5000/matches/${id}`).then((res) => res.json());

    const { teams }: { teams: any[]} = await fetch("http://localhost:5000/teams").then((res) => res.json());
    match = {
        ...match,
        home_team_: teams.find((t) => t.id === match.home_team),
        away_team_: teams.find((t) => t.id === match.away_team)
    }

    if(!match.is_finished) {
        const results = await fetch("http://localhost:5000/matches/results?limit=400").then((res) => res.json());
        const standing = getStanding(teams, results);

        const { fixture } = await predictFixture(match, standing);

        match = {
            ...match,
            analysis: fixture,
            heatmap: []
        }

        for(let i=0; i<8;i++) {
            for(let j=0; j<8;j++) {
                match.heatmap[i * 8 + j] = match.analysis.probabilities.home[i] * match.analysis.probabilities.away[j];
            }
        }
    } else {
        for (const stat_id of match.teams_stats) {
            const { stats } = await fetch(`http://localhost:5000/stats/teams/${stat_id}`).then((res) => res.json());
            if(!match.stats) {
                match.stats = [];
            }
            match = {
                ...match,
                stats: [
                    ...match.stats,
                    stats
                ]
            }
        }
    }

    return (
        <div className="mx-auto p-4 max-w-6xl">
            <h1 className="text-4xl font-bold text-center">Match</h1>
            <div className="mt-5">
                <div className="flex w-fit mx-auto justify-between items-center text-center">
                  {[match.home_team_, match.away_team_].map((team,i) => (
                  <>
                    <div className={`flex flex-1 items-center gap-2 ${i == 1 ? "flex-row-reverse" : ""}`}>
                        <img className="w-10 h-10" src={`https://img.sofascore.com/api/v1/team/${team.sc_id}/image`} />
                        <span className="text-2xl font-bold">{team.name}</span>
                    </div>
                    {i == 0 && <span className="text-2xl flex-1 mx-4 font-bold"> {match.is_finished?match.stats.map((s: any)=>s.goals).join(" - "): "vs"} </span>}
                  </>
                  ))}
                </div>
                {match.analysis && (
                    <>
                        <div style={{
                            background: `linear-gradient(90deg, #0f04 ${match.analysis.home_win_prob * 100}%, #DDD ${match.analysis.home_win_prob * 100}% ${match.analysis.home_win_prob * 100 + match.analysis.draw_prob * 100}%, #f009 ${match.analysis.home_win_prob * 100 + match.analysis.draw_prob * 100}%)`
                        }} className="flex w-2/6 h-2 rounded-full mx-auto px-8 my-2 flex-1 justify-center text-slate-900">
                        </div>
                        <h5 className="text-xl mx-auto w-fit font-bold">H: {(match.analysis.home_win_prob * 100).toFixed(1)}% D: {(match.analysis.draw_prob * 100).toFixed(1)}% A: {(match.analysis.away_win_prob * 100).toFixed(1)}%</h5>
                    </>
                )}
                <h3 className="text-xl font-bold text-center">{new Date(match.played_at * 1000).toLocaleDateString()}</h3>
                <h3 className="text-center">{new Date(match.played_at * 1000).toLocaleTimeString()}</h3>
                {match.analysis && (
                    <section className="flex flex-col items-center my-4">
                        <h2 className="text-2xl font-bold mb-6">Goal Probabilities Heatmap</h2>
                        <div className="flex items-center">
                            <p style={{
                                writingMode: "vertical-lr",
                                textOrientation: "sideways",
                            }} className="text-xl font-bold">Home Team</p>
                            <div className="grid grid-cols-9 gap-4">
                                {match.heatmap.map((prob:any, i:any) =>
                                    <>
                                    {i % 8 == 0 && <div key={i+1000} className="p-4 w-fit ml-auto rounded-md text-base text-right">{Math.floor(i / 8)}</div>}
                                    <div key={i} style={{
                                        backgroundColor: `rgba(0, 255, 0, ${prob * 10})`
                                    }} className="p-4 rounded-md text-sm text-center">
                                        {(prob * 100).toFixed(2)}%
                                    </div></>
                                )}
                                {[...Array(9)].map((_, i) => (
                                    <div key={i+100} className="p-4 w-fit mx-auto rounded-md text-base text-right">{i==0?"":i}</div>
                                ))}
                        </div>
                        </div>
                        <h3 className="text-xl text-center font-bold">Away Team</h3>
                    </section>
                )}
                <section className="flex flex-col my-4">
                    <h3 className="text-xl font-bold">Verbose</h3>
                    <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded-md text-sm">
                        {JSON.stringify(match, null, 4)}
                    </pre>
                </section>
            </div>
        </div>

    )
}