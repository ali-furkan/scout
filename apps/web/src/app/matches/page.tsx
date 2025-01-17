import { FixtureCard } from "@/components/fixture-card";
import { predictFixture } from "@/utils/predict";
import { getStanding } from "@/utils/standing";

export default async function MatchPage() {
    let { matches }: { matches: any[] } = await fetch("http://localhost:5000/matches/fixtures?limit=30").then((res) => res.json());
    const results = await fetch("http://localhost:5000/matches/results?limit=400").then((res) => res.json());
    const { teams }: { teams: any[]} = await fetch("http://localhost:5000/teams").then((res) => res.json());
    const standing = getStanding(teams, results);

    const predictions = await Promise.all(matches.filter(m => (m.played_at * 1000) > Date.now()).map(async (m)=>{
        const { fixture } = await predictFixture(m, standing);

        return {
            ...m,
            home_team_: teams.find((t) => t.id === m.home_team),
            away_team_: teams.find((t) => t.id === m.away_team),
            analysis: fixture
        }
    }))

    return (
        <div className="mx-auto p-4 max-w-6xl">
            <h1 className="text-4xl font-bold text-center">Fixtures</h1>
            <div className="grid grid-cols-1 gap-4 mt-5">
                {predictions.map((p,i) => (
                    <>
                        {(p.round == predictions[i - 1]?.round) ? null : <h3 className="text-xl font-bold text-center">Round - {p.round}</h3>}
                        <FixtureCard key={p.id} match={p} />
                    </>
                ))}
            </div>
        </div>
    )
}