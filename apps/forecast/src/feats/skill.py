import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import SpectralClustering

class SkillFeature:
    name: str
    params: pd.DataFrame
    z_scored_params: pd.DataFrame
    model: SpectralClustering
    scaler: StandardScaler
    cluster_field: str
    results: pd.DataFrame
    cols: list[str]

    def __init__(self, name: str, params:pd.DataFrame, y: pd.DataFrame, cols: list[str]):
        self.name = name
        self.cluster_field = f"{self.name}_cluster"
        self.cols = cols
        self.params = params[self.cols].copy()
        self.results = y
        self.model = SpectralClustering(n_clusters=5, random_state=42)
        self.scale()

    def scale(self):
        self.scaler = StandardScaler()
        self.z_scored_params = self.scaler.fit_transform(self.params)

    def fit(self):
        self.model.fit(self.z_scored_params)

        self.results[self.cluster_field] = self.model.labels_.astype("category")

        self.results["scores_xg_ratio"] = self.results["goals"].sum() / self.results["created_xg"].sum()
        self.results["mean_xg"] = self.results["created_xg"].sum() / len(self.results)
        self.results["mean_goals"] = self.results["goals"].sum() / len(self.results)

    def predict(self, data: pd.DataFrame):
        z_scored_data = self.transform_data([data[self.cols]])

        return self.model.predict(z_scored_data)

ATTACKS_COLS = [
    "big_chances_scored",
    "big_chances_missed",
    "touches_in_box",
    "fouled_in_third",
    "offsides",
]

PASSES_COLS = [
    "accurate_passes",
    "throw_ins",
    "crosses",
    "crosses_success",
    "final_third_entries",
    "final_third_phases",
    "final_third_passes_success",
    "long_passes",
    "long_passes_success",
]

SHOOTS_COLS = [
    "shots_on_target",
    "shots_off_target",
    "blocked_shots",
    "hit_woodwork",
    "shots_inside",
    "shots_outside",
]

DUELS_COLS = [
    "dispossessed",
    "aerial_duels",
    "aerial_duels_success",
    "ground_duels",
    "ground_duels_success",
    "dribbles",
    "dribbles_success",
]

DEAD_BALL_COLS = [
    "free_kicks",
    "corners",
]

DEFENSE_COLS = [
    "tackles",
    "tackles_won",
    "interceptions",
    "recoveries",
    "clearances",
    "errors_leading_to_shot",
    "errors_leading_to_goal",
]

GOALKEEPING_COLS = [
    "saves",
    "goal_prevented",
    "high_claims",
    "punches",
    "goal_kicks",
]


def get_xg_features(df: pd.DataFrame) -> dict["str", SkillFeature]:
    attackFeat = SkillFeature("attacks", "", df[ATTACKS_COLS], ATTACKS_COLS)
    passFeat = SkillFeature("passes", "", df[PASSES_COLS], PASSES_COLS)
    shootFeat = SkillFeature("shoots", "", df[SHOOTS_COLS], SHOOTS_COLS)
    duelFeat = SkillFeature("duels", "", df[DUELS_COLS], DUELS_COLS)
    deadBallFeat = SkillFeature("deadBall", "", df[DEAD_BALL_COLS], DEAD_BALL_COLS)
    defenseFeat = SkillFeature("defense", "", df[DEFENSE_COLS], DEFENSE_COLS)

    gkFeat = SkillFeature("goalkeeping", "", df[GOALKEEPING_COLS], GOALKEEPING_COLS)

    return {
        "attacks": attackFeat,
        "passes": passFeat,
        "shoots": shootFeat,
        "duels": duelFeat,
        "dead_ball": deadBallFeat,
        "defense": defenseFeat,
        "goalkeeping": gkFeat,
    }
