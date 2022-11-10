import traceback

import pandas as pd
from sklearn.impute import SimpleImputer


def count_last_match_goals(X):
    df = X.copy()
    try:
        bet_features = ['B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA', 'LBH', 'LBD', 'LBA', 'WHH', 'WHD', 'WHA']
        df = df.dropna(subset=bet_features, thresh=4)
        df[bet_features] = pd.DataFrame(SimpleImputer().fit_transform(df[bet_features]), columns=bet_features)
        return df
    except Exception:
        traceback.print_exc()
        print('An error occurred')
