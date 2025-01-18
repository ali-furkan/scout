import { FixtureCard } from "@/components/fixture-card";
import { getStanding } from "@/utils/standing";
import { predictFixture } from "@/utils/predict";
import Link from "next/link";


export default async function Home() {
  const { matches }: { matches: any[] } = await fetch("http://localhost:5000/matches/fixtures").then((res) => res.json());
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
    <div className="max-w-6xl mx-auto p-8">
      <h1 className="text-4xl font-extrabold text-center mb-6">Overview</h1>
      <div className="flex justify-between gap-8 flex-col md:flex-row">
        <div className="flex flex-1 flex-col w-full gap-y-4 py-2 rounded-xl">
          <h2 className="text-2xl font-bold">Fixtures</h2>
          <div className="flex flex-col gap-4 px-2">
            {predictions.map((match: any, i) => match.round > 20 && i < 5 && (
              <>
                {match.round == predictions[i - 1]?.round ? null : <h3 className="text-xl font-bold text-center">Round - {match.round}</h3>}
                <FixtureCard key={match.id} match={match} />
              </>
            ))}
            <Link href="/matches">
              <div className="flex items-center mt-4 justify-center dark:text-black text-white bg-black rounded-md px-4 py-1 dark:bg-white hover:opacity-80">
                More Fixture Prediction
              </div>
            </Link>
          </div>
        </div>
        <div className="flex flex-col border rounded-lg px-3 py-4 justify-between my-auto gap-y-2">
          <h2 className="text-2xl text-center font-bold">Standings</h2>
          <div style={{
            gridTemplateColumns: "auto 1fr 1fr 1fr 1fr"
          }} className="grid text-right">
                <span className="mr-4 font-bold text-left">Club</span>
                <span className="font-bold">W</span>
                <span className="font-bold">D</span>
                <span className="font-bold">L</span>
                <span className="flex-1 font-bold">P</span>
            {standing.map((team: any, i) => i<10 && (
              <>
                <div className="flex items-center gap-2">
                  <span className="font-bold">{team.position}.</span>
                  <div className="w-5 h-5">
                    <img className="w-5" src={`https://img.sofascore.com/api/v1/team/${team.sc_id}/image/small`} />
                  </div>
                  <span className="pr-4 text-left text-base">{team.name.length > 18 ? team.name.slice(0,15)+"...": team.name}</span>
                </div>
                <span className="text-lg">{team.wins}</span>
                <span className="text-lg">{team.draws}</span>
                <span className="text-lg">{team.losses}</span>
                <span className="text-lg font-bold">{team.points}</span>
              </>
            ))}
          </div>
          <Link href="/tables">
            <div className="flex items-center mt-4 justify-center dark:text-black text-white bg-black rounded-md px-4 py-1 dark:bg-white hover:opacity-80">
              Show Detail
            </div>
          </Link>
        </div>
      </div>
    </div>
  )
}
