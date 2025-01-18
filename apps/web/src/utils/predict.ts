import { fetchForecast, fetchScraper } from "./fetch";

interface FixtureMatch {
    id: number;
    home_team: string;
    away_team: string;
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
}

interface TeamStrategy {
    attack_cluster: number;
    deadBall_cluster: number;
    duels_cluster: number;
    passes_cluster: number;
    shoots_cluster: number;
    team_label: number;
    defense_cluster: number;
    [key: string]: number; // Add this index signature
}

interface Feature {
    name: string;
    clusters: {
        cat: number,
        scores_xg_ratio: number,
        mean_xg: number,
        mean_goals: number,
    }[]
}

export const predictFixture = async (fixture_match: FixtureMatch, standings: any[]): Promise<{ fixture: any }> => {
    const home_data = await fetchForecast(`/team-strategy/${fixture_match.away_team}`).then((res) => res.json());
    const away_data = await fetchForecast(`/team-strategy/${fixture_match.away_team}`).then((res) => res.json());
    const home_team_strategy: TeamStrategy = home_data.team;
    const away_team_strategy: TeamStrategy = away_data.team;

    const { features }: { features: { [key: string]: Feature } } = await fetchForecast(`/features`).then((res) => res.json());

    const home_team_features = Object.keys(features).map((feature) => {
        const feature_data = features[feature].clusters[home_team_strategy[feature + "_cluster"]];
        const res: { [key: string]: any } = Object.entries(feature_data).reduce((acc, [key, value]) => ({
            ...acc,
            [feature + (key == "cat" ? "_cluster" : key)]: value
        }), {})

        return res;
    });

    const away_team_features = ["attacks","passes","shoots","duels","deadBall"].map((feature) => {
        const feature_data = features[feature].clusters[away_team_strategy[feature + "_cluster"]];
        const res: { [key: string]: any } = Object.entries(feature_data).reduce((acc, [key, value]) => ({
            ...acc,
            [feature+(key=="cat"?"_cluster":key)]: value
        }), {})
        
        return res;
    });

    const time = new Date(fixture_match.played_at * 1000);

    const data = [home_team_features, away_team_features].map((t,i) => ({
        team_label: i == 0 ? home_team_strategy.team_label : away_team_strategy.team_label,
        mif: 0,
        fatigue: 0,
        hours: time.getHours(),
        weekdays: time.getDay(),
        points: standings.find((team) => team.id === (i == 0 ? fixture_match.home_team: fixture_match.away_team)).points,
        ...t.reduce((acc, curr) => ({ ...acc, ...curr }), {}),
    }));

    const { prediction } = await fetchForecast("/stats/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ "params": data })
    }).then((res) => res.json());

    const result = await fetchForecast("/fixture/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ "home": prediction[0], "away": prediction[1] })
    }).then((res) => res.json());

    return result;
}