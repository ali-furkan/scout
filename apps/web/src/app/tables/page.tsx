import { getStanding } from "@/utils/standing";
import Link from "next/link";

export default async function TablePage() {
    const results = await fetch("http://localhost:5000/matches/results?limit=400").then((res) => res.json());
    const { teams }: { teams: any[]} = await fetch("http://localhost:5000/teams").then((res) => res.json());
    const standing = getStanding(teams, results);

    return (
        <div className="mx-auto p-4 max-w-6xl">
            <h1 className="text-4xl font-bold">Tables</h1>
            <div className="flex flex-col ">
                <div className="flex justify-between items-center">
                    <h3 className="text-xl font-bold text-slate-800 dark:text-slate-500">Premier League Actual</h3>
                    <Link href={"/pred-table"}>
                        <div className="flex items-center w-fit mt-4 justify-center dark:text-black text-white bg-black rounded-md px-4 py-1 dark:bg-white hover:opacity-80">
                            Go to Prediction
                        </div>
                    </Link>
                </div>
                <div style={{ gridTemplateColumns: "3fr 1fr" }} className="grid gap-4 mt-5 w-full">
                    <span className="mr-4 font-bold text-left">Club</span>
                    <div className="flex gap-x-2">
                        <span className="font-bold">W</span>
                        <span className="font-bold">D</span>
                        <span className="font-bold">L</span>
                        <span className="flex-1 font-bold">P</span>
                    </div>
                    {standing.map((team: any, i) => (
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