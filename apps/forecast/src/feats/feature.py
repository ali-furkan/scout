import pandas as pd

class Feature:
    name: str
    description: str
    params: pd.DataFrame

    def __init__(self, name, params, description=""):
        self.name = name
        self.description = description
        self.params = params