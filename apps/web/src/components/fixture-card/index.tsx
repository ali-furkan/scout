import Link from 'next/link';
import React from "react"

interface FixtureCardProps {
    match: {
        id: number;
        home_team_: {
            name: string;
            sc_id: number;
        };
        away_team_: {
            name: string;
            sc_id: number;
        };
        analysis: {
            home_win_prob: number;
            draw_prob: number;
            away_win_prob: number;
        };
        played_at: number;
    };
}

export const FixtureCard: React.FC<FixtureCardProps> = ({ match }) => {
    return (
        <Link href={`/matches/${match.id}`}>
            <div className="flex cursor-pointer items-center justify-between p-3 border-gray-200 rounded-xl">
                <div className="flex items-left gap-2 flex-col flex-1">
                    <div className="flex items-center">
                        <img className="w-8 mr-4" src={`https://img.sofascore.com/api/v1/team/${match.home_team_.sc_id}/image`} />
                        <span className="text-xl text-left font-bold"> {match.home_team_.name} </span>
                    </div>
                    <div className="flex items-center">
                        <img className="w-8 mr-4" src={`https://img.sofascore.com/api/v1/team/${match.away_team_.sc_id}/image`} />
                        <span className="text-xl text-left font-bold"> {match.away_team_.name} </span>
                    </div>
                </div>
                {match.analysis && (
                    <div className="flex flex-1 justify-center">
                        <span className="text-sm font-bold">H: {Math.round(match.analysis.home_win_prob * 100)}% D: {Math.round(match.analysis.draw_prob * 100)}% A: {Math.round(match.analysis.away_win_prob * 100)}%</span>
                    </div>
                )}
                <div className="flex flex-1 flex-col items-center justify-center">
                    <span className="text-lg">{new Date(match.played_at * 1000).toLocaleTimeString()} </span>
                    <span className="">{new Date(match.played_at * 1000).toDateString()}</span>
                </div>
            </div>
        </Link>
    );
}