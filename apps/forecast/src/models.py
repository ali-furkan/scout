from utils import handle_points
from feats.mif import create_mif_model
from sklearn.model_selection import cross_val_score, KFold

def prepare_models():
    # MIF model
    matches = handle_points(matches)

    mif_data = matches[
        ["home_team", "away_team", "home_points", "away_points", "attendances"]
    ].copy()

    mif_model = create_mif_model(mif_data)

    return mif_model


def model_fit_predict(model, X_train, X_test, y_train):
    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    return pred

def create_base_models(mparams: dict=None, r_num: int=42) -> list:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from lightgbm import LGBMRegressor

    models = [
        {
            "model": LGBMRegressor(random_state=r_num),
            "name": "xg_lgbm",
        },
        {
            "model": RandomForestRegressor(random_state=r_num),
            "name": "xg_rf",
        },
        {
            "model": GradientBoostingRegressor(random_state=r_num),
            "name": "xg_gb",
        },
    ]

    for m in models:
        if m["name"] in mparams.keys() if mparams else False:
            m["model"].set_params(**mparams[m["name"]])


    return models

def opt_base_models(models: list,X_train, y_train) -> list[dict[str, any]]:
    from skopt import BayesSearchCV

    grid = {
        "n_estimators": (100, 500),
        "max_depth": (3, 21),
        "subsample": (0.6, 1.0),
        "learning_rate": (0.01, 0.3, 'log-uniform'),
    }

    results = []
    for model in models:
        opt = BayesSearchCV(
            estimator=model,
            search_spaces=grid,
            scoring="neg_mean_squared_error",
            cv=5,
            n_iter=24,
            n_jobs=-1,
        )
        opt.fit(X_train, y_train)
        model.set_params(**opt.best_params_)

        results.append({
            "name": model["name"],
            "cv_results": opt.cv_results_,
            "best_params": opt.best_params_,
            "best_score": opt.best_score_,  
        })

    return results

def test_cv_model(model, X_train, y_train) -> float:
    kfold = KFold(5, shuffle=True, random_state=42)
    cv = cross_val_score(
        model,
        X_train,
        y_train,
        cv=kfold,
        scoring="neg_mean_squared_error",
    )

    return abs(cv.mean())



from sklearn.ensemble import StackingRegressor
def create_stack_model(models: list) -> StackingRegressor:
    from sklearn.ensemble import RandomForestRegressor

    stack = StackingRegressor(
        estimators=[(m["name"], m["model"]) for m in models],
        final_estimator=RandomForestRegressor(max_depth=10,random_state=42),
        n_jobs=-1,
        cv=5,
        passthrough=False,
    )

    return stack
