import traceback

import numpy as np
import pandas as pd

from preprocess.football_utils import create_new_df_from_xml


def xml_to_feature_possession(X):
    df = X.copy()
    columns_possession = ['awaypos', 'homepos', 'subtype', 'elapsed']
    new_columns_possession = ['awaypos', 'homepos', 'subtype', 'elapsed']
    df_possession = create_new_df_from_xml(df, 'possession', columns_possession, new_columns_possession)

    df_possession[['awaypos', 'homepos']] = df_possession[['awaypos', 'homepos']].fillna(0).astype('int')
    df_possession[['awaypos', 'homepos']] = df_possession[['awaypos', 'homepos']].replace(0, np.nan)
    df_possession['awaypos'] = df_possession['awaypos'].fillna(
        df_possession.groupby('match_api_id')['awaypos'].transform('mean'))
    df_possession['homepos'] = df_possession['homepos'].fillna(
        df_possession.groupby('match_api_id')['homepos'].transform('mean'))
    df_possession[['awaypos', 'homepos']] = df_possession[['awaypos', 'homepos']].astype('int')

    df_possession = df_possession.loc[(df_possession['elapsed'] == '90') | df_possession['elapsed'].isna()]
    df_possession = df_possession.groupby(by=['match_api_id'])[['awaypos', 'homepos']].mean().astype(int)
    df_possession = df_possession.reset_index(level=0)

    return pd.merge(df, df_possession, how='left', on='match_api_id')


def fill_nan_possession(X, X_nan):
    for index, row in X_nan.iterrows():
        home_team = row['home_team']
        away_team = row['away_team']

        mask_all_matches_between_teams = ((X['home_team'] == home_team) | (X['away_team'] == home_team)) & \
                                         ((X['home_team'] == away_team) | (X['away_team'] == away_team))
        all_matches_between_teams = X.loc[mask_all_matches_between_teams]

        home_possessions = []
        away_possessions = []

        for idx, r in all_matches_between_teams.iterrows():
            get_possession(home_possessions, home_team, r)
            get_possession(away_possessions, away_team, r)

        if (len(home_possessions) == 0) | (len(away_possessions) == 0):
            continue
        else:
            avg_possession_home = sum(home_possessions) / len(home_possessions)
            avg_possession_away = sum(away_possessions) / len(away_possessions)
            X.loc[X['match_api_id'] == row['match_api_id'], 'homepos'] = int(avg_possession_home)
            X.loc[X['match_api_id'] == row['match_api_id'], 'awaypos'] = int(avg_possession_away)

    X['awaypos'] = X['awaypos'].fillna(X.groupby(['away_team'])['awaypos'].transform('mean'))
    X['homepos'] = X['homepos'].fillna(X.groupby(['home_team'])['homepos'].transform('mean'))

    X['awaypos'] = X['awaypos'].fillna(X.groupby(['league_name'])['awaypos'].transform('mean'))
    X['homepos'] = X['homepos'].fillna(X.groupby(['league_name'])['homepos'].transform('mean'))

    return X


def get_possession(possessions, team, r):
    if (r['home_team'] == team) & (not pd.isna(r['homepos'])):
        possessions.append(r['homepos'])
    elif (r['away_team'] == team) & (not pd.isna(r['awaypos'])):
        possessions.append(r['awaypos'])


def get_last_match_possession(X, teams):
    df = X.copy()
    try:
        for team in teams:
            mask_team_matches = (df['home_team'] == team) | (df['away_team'] == team)
            matches = df.loc[mask_team_matches]
            matches = matches.sort_values(by='date')

            for index, row in matches.iterrows():
                previous_match_possession = row['homepos'] if team == row['home_team'] else row['awaypos']
                last_match = matches.loc[matches['match_api_id'].shift(1) == row['match_api_id']].dropna(how='all')

                if not last_match.empty:
                    if team == last_match['home_team'].values:
                        df.loc[df['match_api_id'] == last_match['match_api_id'].values[0],
                               'last_match_possession_home'] = previous_match_possession
                    else:
                        df.loc[df['match_api_id'] == last_match['match_api_id'].values[0],
                               'last_match_possession_away'] = previous_match_possession

        df['last_match_possession_away'] = df['last_match_possession_away'].fillna(
            df.groupby(['away_team'])['last_match_possession_away'].transform('mean'))
        df['last_match_possession_home'] = df['last_match_possession_home'].fillna(
            df.groupby(['home_team'])['last_match_possession_home'].transform('mean'))

        df['last_match_possession_away'] = df['last_match_possession_away'].fillna(
            df.groupby(['league_name'])['last_match_possession_away'].transform('mean'))
        df['last_match_possession_home'] = df['last_match_possession_home'].fillna(
            df.groupby(['league_name'])['last_match_possession_home'].transform('mean'))

        df.last_match_possession_home = df.last_match_possession_home.astype(int)
        df.last_match_possession_away = df.last_match_possession_away.astype(int)
        return df
    except Exception:
        traceback.print_exc()
        print('An error occurred')

