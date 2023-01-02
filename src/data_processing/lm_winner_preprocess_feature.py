import logging
import traceback

import pandas as pd

from src.data_processing import football_utils

logger = logging.getLogger(__name__)


def count_victories_against_eachother(X):
    try:
        df = X.copy()
        for index, row in df.iterrows():
            home_team = row['home_team']
            away_team = row['away_team']

            mask_all_matches_between_teams = ((df['home_team'] == home_team) | (df['away_team'] == home_team)) & (
                    (df['home_team'] == away_team) | (df['away_team'] == away_team))
            all_matches_between_teams = df.loc[mask_all_matches_between_teams]

            for idx, r in all_matches_between_teams.iterrows():
                last_match = all_matches_between_teams.loc[
                    all_matches_between_teams['match_api_id'].shift(1) == r['match_api_id']].dropna(how='all')
                if not last_match.empty:
                    lm_winner = football_utils.get_winner(r)
                    match_api_id_ = df['match_api_id'] == last_match.iloc[0]['match_api_id']
                    df.loc[match_api_id_, 'lm_winner'] = lm_winner
        return df
    except Exception:
        traceback.print_exc()
        print('An error occurred')


def fill_nan_last_match_winner(X):
    try:
        df = X.copy()
        df_detailed_matches_nan_lm_winner = df.loc[df.lm_winner.isna()]

        for index, row in df_detailed_matches_nan_lm_winner.iterrows():
            home_team = row['home_team']
            away_team = row['away_team']

            mask_all_matches_between_teams = ((df['home_team'] == home_team) | (
                    df['away_team'] == home_team)) & ((df['home_team'] == away_team) | (df['away_team'] == away_team))

            all_matches_between_teams = df.loc[mask_all_matches_between_teams]

            if all_matches_between_teams.lm_winner.value_counts().size != 0:
                lm_winner = all_matches_between_teams.lm_winner.value_counts().idxmax()
                if pd.isna(lm_winner):
                    lm_winner = football_utils.get_winner(row)
                df.loc[df['match_api_id'] == row['match_api_id'], 'lm_winner'] = lm_winner
            else:
                if df['points_home'] > df['points_away']:
                    lm_winner = df['home_team']
                    df.loc[df['match_api_id'] == row['match_api_id'], 'lm_winner'] = lm_winner
                elif df['points_home'] < df['points_away']:
                    lm_winner = df['home_team']
                    df.loc[df['match_api_id'] == row['match_api_id'], 'lm_winner'] = lm_winner
                else:
                    df.loc[df['match_api_id'] == row['match_api_id'], 'lm_winner'] = 0

        df.lm_winner = df.lm_winner.astype('int')
        return df
    except Exception:
        traceback.print_exc()
        print('An error occurred')
