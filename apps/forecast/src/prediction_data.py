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
