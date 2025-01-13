import Image from "next/image";
import Link from "next/link";


export default async function Home() {
  const data = await fetch("http://localhost:5000/matches/fixtures").then((res) => res.json());
  const { teams } = await fetch("http://localhost:5000/teams").then((res) => res.json());
  const analysis = await fetch("http://localhost:3000/matches.json").then((res) => res.json());
  const matches = await Promise.all(data.matches.map(async (match: any) => {
    const home_team = teams.find((team: any) => team.id === match.home_team);
    const away_team = teams.find((team: any) => team.id === match.away_team);

    return {
      ...match,
      home_team_: home_team,
      away_team_: away_team,
      analysis: analysis.find((a: any) => a.id === match.id)
    };
  }));

  return (
    <div className="flex flex-col items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <h1 className="text-4xl">Scoutview</h1>
      <h2 className="text-2xl font-bold">Fixture Prediction</h2>
      <ul>
        {matches.map((match: any, i) => match.round > 20 && (
        <>
            {match.round == matches[i - 1]?.round ? null : <h3 className="text-xl font-bold text-center">Round - {match.round}</h3>}
            <Link href={`/matches/${match.id}`}>
              <li key={match.id} className="flex flex-col cursor-pointer items-center justify-center p-7 my-4 border border-gray-200 rounded-xl">
                <div>
                  <span className="text-3xl font-bold text-center"><span style={{
                    backgroundColor: match.home_team_.colors.primary,
                    width: "10px",
                    height: "10px",
                  }}></span>{match.home_team_.name} - {match.away_team_.name}</span>
                </div>
                {match.analysis && (
                  <div>
                    <span className="text-sm font-bold">H: {Math.round(match.analysis.home_win_prob * 100)}% D: {Math.round(match.analysis.draw_prob * 100)}% A: {Math.round(match.analysis.away_win_prob * 100)}%</span>
                  </div>
                )}
                <div className="flex flex-col items-center justify-center">
                  <span className="text-lg">{new Date(match.played_at * 1000).toLocaleTimeString()} </span>
                  <span className="">{new Date(match.played_at * 1000).toDateString()}</span>
                </div>
              </li>
            </Link>
        </>
        ))}
      </ul>
    </div>
  );
}
