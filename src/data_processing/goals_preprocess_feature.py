import logging
import traceback

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

def count_last_match_goals(X, teams):
    df = X.copy()
    try:
        for team in teams:
            mask_team_matches = (df['home_team'] == team) | (df['away_team'] == team)
            matches = df.loc[mask_team_matches]
            matches = matches.sort_values(by='date')

            for index, row in matches.iterrows():
                previous_match_goals = row['home_team_goal'] if team == row['home_team'] else row['away_team_goal']
                last_match = matches.loc[matches['match_api_id'].shift(1) == row['match_api_id']].dropna(how='all')
                if not last_match.empty:
                    if team == last_match['home_team'].values:
                        df.loc[
                            df['match_api_id'] == last_match.iloc[0][
                                'match_api_id'], 'lm_goals_home'] = previous_match_goals
                    else:
                        df.loc[
                            df['match_api_id'] == last_match.iloc[0][
                                'match_api_id'], 'lm_goals_away'] = previous_match_goals
        return df
    except Exception:
        traceback.print_exc()
        print('An error occurred')


def count_average_goals_from_last_n_matches(X, teams, n=5):
    try:
        df = X.copy()
        for team in teams:
            mask_find_team_matches = (df['home_team'] == team) | (
                    df['away_team'] == team)
            team_matches = df.loc[mask_find_team_matches]
            team_matches = team_matches.sort_values(by='date')

            for index, row in team_matches.iterrows():
                mask_home = ((team_matches['home_team'] == row['home_team']) & (team_matches['date'] < row['date']))
                mask_away = ((team_matches['away_team'] == row['away_team']) & (team_matches['date'] < row['date']))
                mask_both = (team_matches['date'] < row['date'])

                avg_l5m_hh = team_matches.loc[mask_home].iloc[-n:]['home_team_goal'].mean()
                avg_l5m_aa = team_matches.loc[mask_away].iloc[-n:]['away_team_goal'].mean()
                l5_m = team_matches.loc[mask_both].iloc[-n:]

                goals = []

                for idx, r in l5_m.iterrows():
                    if r['home_team'] == team:
                        goals.append(r['home_team_goal'])
                    else:
                        goals.append(r['away_team_goal'])

                avg_l5_m = np.nan if len(goals) == 0 else sum(goals) / len(goals)
                if team == row['home_team']:
                    if pd.isna(avg_l5m_hh):
                        avg_l5m_hh = row['home_team_goal']
                    df.loc[df['match_api_id'] == row['match_api_id'], f'avg_l{n}m_hh'] = avg_l5m_hh
                    df.loc[df['match_api_id'] == row['match_api_id'], f'avg_l{n}m_h'] = avg_l5_m
                else:
                    if pd.isna(avg_l5m_aa):
                        avg_l5m_aa = row['away_team_goal']
                    df.loc[df['match_api_id'] == row['match_api_id'], f'avg_l{n}m_aa'] = avg_l5m_aa
                    df.loc[df['match_api_id'] == row['match_api_id'], f'avg_l{n}m_a'] = avg_l5_m
        return df
    except Exception:
        traceback.print_exc()
        print('An error occurred')
