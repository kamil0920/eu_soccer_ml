import numpy as np
import pandas as pd

from preprocess.football_utils import create_new_df_from_xml


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
    except Exception as e:
        print('An error occurred:', e)


def count_average_goals_from_last_n_matches(X, teams, n=5):
    df = X.copy()
    try:
        for team in teams:
            mask_find_team_matches = (df['home_team'] == team) | (
                    df['away_team'] == team)
            team_matches = df.loc[mask_find_team_matches]
            team_matches = team_matches.sort_values(by='date')

            for index, row in team_matches.iterrows():
                mask_home = ((team_matches['home_team'] == row['home_team']) & (team_matches['date'] < row['date']))
                mask_away = ((team_matches['away_team'] == row['away_team']) & (team_matches['date'] < row['date']))
                mask_both = (team_matches['date'] < row['date'])

                avg_l5m_hh = team_matches.loc[mask_home].iloc[-5:]['home_team_goal'].mean()
                avg_l5m_aa = team_matches.loc[mask_away].iloc[-5:]['away_team_goal'].mean()
                l5_m = team_matches.loc[mask_both].iloc[-5:]

                goals = []

                for idx, r in l5_m.iterrows():
                    if r['home_team'] == team:
                        goals.append(r['home_team_goal'])
                    else:
                        goals.append(r['away_team_goal'])

                avg_l5_m = np.nan if len(goals) == 0 else sum(goals) / len(goals)
                if team == row['home_team']:
                    if pd.isna(avg_l5m_aa):
                        avg_l5m_aa = row['home_team_goal']
                    df.loc[
                        df['match_api_id'] == row['match_api_id'], 'avg_l5m_hh'] = avg_l5m_hh
                    df.loc[
                        df['match_api_id'] == row['match_api_id'], 'avg_l5m_h'] = avg_l5_m
                else:
                    if pd.isna(avg_l5m_aa):
                        avg_l5m_aa = row['away_team_goal']
                    df.loc[
                        df['match_api_id'] == row['match_api_id'], 'avg_l5m_aa'] = avg_l5m_aa
                    df.loc[
                        df['match_api_id'] == row['match_api_id'], 'avg_l5m_a'] = avg_l5_m
        return df
    except Exception as e:
        print('An error occurred:', e)


def count_streak_wins(X, teams):
    df = X.copy()
    try:
        for team in teams:
            mask_team_matches = (df['home_team'] == team) | (df['away_team'] == team)
            team_matches = df.loc[mask_team_matches]
            team_matches = team_matches.sort_values(by='date', ascending=False)

            for index, row in team_matches.iterrows():
                mask_both = (team_matches['date'] < row['date'])
                matches_filtering_by_date = team_matches.loc[mask_both]
                win_counter = 0

                for idx in range(len(matches_filtering_by_date)):
                    if team == matches_filtering_by_date.iloc[idx]['home_team']:
                        match_goals = matches_filtering_by_date[['home_team_goal', 'away_team_goal']].iloc[idx]
                        if match_goals.loc['home_team_goal'] > match_goals.loc['away_team_goal']:
                            win_counter = win_counter + 1
                        else:
                            break
                    else:
                        match_goals = matches_filtering_by_date[['home_team_goal', 'away_team_goal']].iloc[idx]
                        if match_goals.loc['home_team_goal'] < match_goals.loc['away_team_goal']:
                            win_counter = win_counter + 1
                        else:
                            break
                if team == row['home_team']:
                    df.loc[
                        df['match_api_id'] == row['match_api_id'], 'streak_wh'] = win_counter
                else:
                    df.loc[
                        df['match_api_id'] == row['match_api_id'], 'streak_wa'] = win_counter
        return df
    except Exception as e:
        print('An error occurred:', e)


def count_streak_lose(X, teams):
    df = X.copy()
    try:
        for team in teams:
            mask_team_matches = (df['home_team'] == team) | (df['away_team'] == team)
            team_matches = df.loc[mask_team_matches]
            team_matches = team_matches.sort_values(by='date', ascending=False)

            for index, row in team_matches.iterrows():
                mask_both = (team_matches['date'] < row['date'])
                matches_filtering_by_date = team_matches.loc[mask_both]
                lose_counter = 0

                for idx in range(len(matches_filtering_by_date)):
                    if team == matches_filtering_by_date.iloc[idx]['home_team']:
                        match_goals = matches_filtering_by_date[['home_team_goal', 'away_team_goal']].iloc[idx]
                        if match_goals.loc['home_team_goal'] > match_goals.loc['away_team_goal']:
                            break
                        else:
                            lose_counter = lose_counter + 1
                    else:
                        match_goals = matches_filtering_by_date[['home_team_goal', 'away_team_goal']].iloc[idx]
                        if match_goals.loc['home_team_goal'] < match_goals.loc['away_team_goal']:
                            break
                        else:
                            lose_counter = lose_counter + 1

                if team == row['home_team']:
                    df.loc[df['match_api_id'] == row['match_api_id'], 'streak_lh'] = lose_counter
                else:
                    df.loc[df['match_api_id'] == row['match_api_id'], 'streak_la'] = lose_counter
        return df
    except Exception as e:
        print('An error occurred:', e)


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

        mask_all_matches_between_teams = ((X['home_team'] == home_team) | (X['away_team'] == home_team)) &\
                                         ((X['home_team'] == away_team) | (X['away_team'] == away_team))
        all_matches_between_teams = X.loc[mask_all_matches_between_teams]

        home_possessions = []
        away_possessions = []

        for idx, r in all_matches_between_teams.iterrows():
            # home_possessions.append(get_possession(r['home_team'], r))
            # away_possessions.append(get_possession(r['away_team'], r))
            get_possession(home_possessions, home_team, r)
            get_possession(away_possessions, away_team, r)

        if (len(home_possessions) == 0) | (len(away_possessions) == 0):
            continue
            # res = X.drop(X[X.match_api_id == row.match_api_id].index)
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
