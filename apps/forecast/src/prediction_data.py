import pandas as pd
from feats.skill import SkillFeature

import numpy as np

def prepare_fixture():
    pass


def team_strategy_predict(team_label: int, X: pd.DataFrame, features: dict[str,SkillFeature]) -> pd.DataFrame:
    matches = X.copy().loc[X["team_label"] == team_label]
    res = {}
    res["team_label"] = int(team_label)
    for f in features.values():
        dominant_cat = matches[f.cluster_field].tail(5).value_counts().idxmax()
        avg_cat = matches[f.cluster_field].value_counts().idxmax()

        c0 = f.model.cluster_centers_[dominant_cat]
        c1 = f.model.cluster_centers_[avg_cat]

        new_point = c0 * 0.6 + c1 * 0.4

        d = np.linalg.norm(f.model.cluster_centers_ - new_point, axis=1)

        res[f.cluster_field] = int(np.argmin(d))

    print(res)
    return res


    


def match_strategy_predict(
    stats: pd.DataFrame, match_data: pd.DataFrame, feats: list[SkillFeature]
) -> pd.DataFrame:
    home_team = stats.loc[stats["team"] == match_data["home_team"]]
    away_team = stats.loc[stats["team"] == match_data["away_team"]]

    # Initialize result DataFrame with proper index
    res = pd.DataFrame(index=range(2))  # 2 rows for home and away teams

    for i, t in enumerate([home_team, away_team]):
        # Fill NaN values with mean for numerical columns
        t = t.fillna(t.mean(numeric_only=True))
        t_mean = t.mean(numeric_only=True)
        m = match_data
        t_top_5_mean = t.nlargest(5, "played_at").mean(numeric_only=True)
        t_predict = t_mean * 0.5 + t_top_5_mean * 0.5

        for f in feats:
            feature_data = t_predict[f.cols].fillna(t_predict[f.cols].mean())
            predicted_cat = f.predict(pd.DataFrame([feature_data]))
            # Convert prediction to scalar value before assignment
            res.at[i, f"{f.name}_cluster"] = predicted_cat[0]

    return res
