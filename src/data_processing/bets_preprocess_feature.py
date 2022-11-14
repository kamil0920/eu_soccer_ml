import logging
import traceback

logger = logging.getLogger(__name__)

def fill_nan_bets(X):
    df = X.copy()
    try:
        df.drop(['IWH', 'IWA', 'IWD'], axis=1, inplace=True)
        bet_features = ['B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA', 'LBH', 'LBD', 'LBA', 'WHH', 'WHD', 'WHA']
        df = df.dropna(subset=bet_features, thresh=4)
        df[bet_features] = df[bet_features].apply(lambda x: x.fillna(x.mean()), axis=1)
        return df
    except Exception:
        traceback.print_exc()
        print('An error occurred')
