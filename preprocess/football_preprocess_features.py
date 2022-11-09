import traceback

# import numpy as np
# import pandas as pd
#
# from preprocess import football_utils
# from preprocess.football_utils import create_new_df_from_xml
#
#
# def count_last_match_goals(X, teams):
#     df = X.copy()
#     try:
#         for team in teams:
#             mask_team_matches = (df['home_team'] == team) | (df['away_team'] == team)
#             matches = df.loc[mask_team_matches]
#             matches = matches.sort_values(by='date')
#
#             for index, row in matches.iterrows():
#                 previous_match_goals = row['home_team_goal'] if team == row['home_team'] else row['away_team_goal']
#                 last_match = matches.loc[matches['match_api_id'].shift(1) == row['match_api_id']].dropna(how='all')
#                 if not last_match.empty:
#                     if team == last_match['home_team'].values:
#                         df.loc[
#                             df['match_api_id'] == last_match.iloc[0][
#                                 'match_api_id'], 'lm_goals_home'] = previous_match_goals
#                     else:
#                         df.loc[
#                             df['match_api_id'] == last_match.iloc[0][
#                                 'match_api_id'], 'lm_goals_away'] = previous_match_goals
#         return df
#     except Exception:
#         traceback.print_exc()
#         print('An error occurred')
#
#
# def count_average_goals_from_last_n_matches(X, teams, n=5):
#     df = X.copy()
#     try:
#         for team in teams:
#             mask_find_team_matches = (df['home_team'] == team) | (
#                     df['away_team'] == team)
#             team_matches = df.loc[mask_find_team_matches]
#             team_matches = team_matches.sort_values(by='date')
#
#             for index, row in team_matches.iterrows():
#                 mask_home = ((team_matches['home_team'] == row['home_team']) & (team_matches['date'] < row['date']))
#                 mask_away = ((team_matches['away_team'] == row['away_team']) & (team_matches['date'] < row['date']))
#                 mask_both = (team_matches['date'] < row['date'])
#
#                 avg_l5m_hh = team_matches.loc[mask_home].iloc[-n:]['home_team_goal'].mean()
#                 avg_l5m_aa = team_matches.loc[mask_away].iloc[-n:]['away_team_goal'].mean()
#                 l5_m = team_matches.loc[mask_both].iloc[-n:]
#
#                 goals = []
#
#                 for idx, r in l5_m.iterrows():
#                     if r['home_team'] == team:
#                         goals.append(r['home_team_goal'])
#                     else:
#                         goals.append(r['away_team_goal'])
#
#                 avg_l5_m = np.nan if len(goals) == 0 else sum(goals) / len(goals)
#                 if team == row['home_team']:
#                     if pd.isna(avg_l5m_hh):
#                         avg_l5m_hh = row['home_team_goal']
#                     df.loc[df['match_api_id'] == row['match_api_id'], 'avg_l5m_hh'] = avg_l5m_hh
#                     df.loc[df['match_api_id'] == row['match_api_id'], 'avg_l5m_h'] = avg_l5_m
#                 else:
#                     if pd.isna(avg_l5m_aa):
#                         avg_l5m_aa = row['away_team_goal']
#                     df.loc[df['match_api_id'] == row['match_api_id'], 'avg_l5m_aa'] = avg_l5m_aa
#                     df.loc[df['match_api_id'] == row['match_api_id'], 'avg_l5m_a'] = avg_l5_m
#         return df
#     except Exception:
#         traceback.print_exc()
#         print('An error occurred')
#
#
# def count_streak_wins(X, teams):
#     df = X.copy()
#     try:
#         for team in teams:
#             mask_team_matches = (df['home_team'] == team) | (df['away_team'] == team)
#             team_matches = df.loc[mask_team_matches]
#             team_matches = team_matches.sort_values(by='date', ascending=False)
#
#             for index, row in team_matches.iterrows():
#                 mask_both = (team_matches['date'] < row['date'])
#                 matches_filtering_by_date = team_matches.loc[mask_both]
#                 win_counter = 0
#
#                 for idx in range(len(matches_filtering_by_date)):
#                     if team == matches_filtering_by_date.iloc[idx]['home_team']:
#                         match_goals = matches_filtering_by_date[['home_team_goal', 'away_team_goal']].iloc[idx]
#                         if match_goals.loc['home_team_goal'] > match_goals.loc['away_team_goal']:
#                             win_counter = win_counter + 1
#                         else:
#                             break
#                     else:
#                         match_goals = matches_filtering_by_date[['home_team_goal', 'away_team_goal']].iloc[idx]
#                         if match_goals.loc['home_team_goal'] < match_goals.loc['away_team_goal']:
#                             win_counter = win_counter + 1
#                         else:
#                             break
#                 if team == row['home_team']:
#                     df.loc[
#                         df['match_api_id'] == row['match_api_id'], 'streak_wh'] = win_counter
#                 else:
#                     df.loc[
#                         df['match_api_id'] == row['match_api_id'], 'streak_wa'] = win_counter
#         return df
#     except Exception:
#         traceback.print_exc()
#         print('An error occurred')
#
#
# def count_streak_lose(X, teams):
#     df = X.copy()
#     try:
#         for team in teams:
#             mask_team_matches = (df['home_team'] == team) | (df['away_team'] == team)
#             team_matches = df.loc[mask_team_matches]
#             team_matches = team_matches.sort_values(by='date', ascending=False)
#
#             for index, row in team_matches.iterrows():
#                 mask_both = (team_matches['date'] < row['date'])
#                 matches_filtering_by_date = team_matches.loc[mask_both]
#                 lose_counter = 0
#
#                 for idx in range(len(matches_filtering_by_date)):
#                     if team == matches_filtering_by_date.iloc[idx]['home_team']:
#                         match_goals = matches_filtering_by_date[['home_team_goal', 'away_team_goal']].iloc[idx]
#                         if match_goals.loc['home_team_goal'] > match_goals.loc['away_team_goal']:
#                             break
#                         else:
#                             lose_counter = lose_counter + 1
#                     else:
#                         match_goals = matches_filtering_by_date[['home_team_goal', 'away_team_goal']].iloc[idx]
#                         if match_goals.loc['home_team_goal'] < match_goals.loc['away_team_goal']:
#                             break
#                         else:
#                             lose_counter = lose_counter + 1
#
#                 if team == row['home_team']:
#                     df.loc[df['match_api_id'] == row['match_api_id'], 'streak_lh'] = lose_counter
#                 else:
#                     df.loc[df['match_api_id'] == row['match_api_id'], 'streak_la'] = lose_counter
#         return df
#     except Exception:
#         traceback.print_exc()
#         print('An error occurred')
#
#
# def xml_to_feature_possession(X):
#     df = X.copy()
#     columns_possession = ['awaypos', 'homepos', 'subtype', 'elapsed']
#     new_columns_possession = ['awaypos', 'homepos', 'subtype', 'elapsed']
#     df_possession = create_new_df_from_xml(df, 'possession', columns_possession, new_columns_possession)
#
#     df_possession[['awaypos', 'homepos']] = df_possession[['awaypos', 'homepos']].fillna(0).astype('int')
#     df_possession[['awaypos', 'homepos']] = df_possession[['awaypos', 'homepos']].replace(0, np.nan)
#     df_possession['awaypos'] = df_possession['awaypos'].fillna(
#         df_possession.groupby('match_api_id')['awaypos'].transform('mean'))
#     df_possession['homepos'] = df_possession['homepos'].fillna(
#         df_possession.groupby('match_api_id')['homepos'].transform('mean'))
#     df_possession[['awaypos', 'homepos']] = df_possession[['awaypos', 'homepos']].astype('int')
#
#     df_possession = df_possession.loc[(df_possession['elapsed'] == '90') | df_possession['elapsed'].isna()]
#     df_possession = df_possession.groupby(by=['match_api_id'])[['awaypos', 'homepos']].mean().astype(int)
#     df_possession = df_possession.reset_index(level=0)
#
#     return pd.merge(df, df_possession, how='left', on='match_api_id')
#
#
# def fill_nan_possession(X, X_nan):
#     for index, row in X_nan.iterrows():
#         home_team = row['home_team']
#         away_team = row['away_team']
#
#         mask_all_matches_between_teams = ((X['home_team'] == home_team) | (X['away_team'] == home_team)) & \
#                                          ((X['home_team'] == away_team) | (X['away_team'] == away_team))
#         all_matches_between_teams = X.loc[mask_all_matches_between_teams]
#
#         home_possessions = []
#         away_possessions = []
#
#         for idx, r in all_matches_between_teams.iterrows():
#             get_possession(home_possessions, home_team, r)
#             get_possession(away_possessions, away_team, r)
#
#         if (len(home_possessions) == 0) | (len(away_possessions) == 0):
#             continue
#         else:
#             avg_possession_home = sum(home_possessions) / len(home_possessions)
#             avg_possession_away = sum(away_possessions) / len(away_possessions)
#             X.loc[X['match_api_id'] == row['match_api_id'], 'homepos'] = int(avg_possession_home)
#             X.loc[X['match_api_id'] == row['match_api_id'], 'awaypos'] = int(avg_possession_away)
#
#     X['awaypos'] = X['awaypos'].fillna(X.groupby(['away_team'])['awaypos'].transform('mean'))
#     X['homepos'] = X['homepos'].fillna(X.groupby(['home_team'])['homepos'].transform('mean'))
#
#     X['awaypos'] = X['awaypos'].fillna(X.groupby(['league_name'])['awaypos'].transform('mean'))
#     X['homepos'] = X['homepos'].fillna(X.groupby(['league_name'])['homepos'].transform('mean'))
#
#     return X
#
#
# def get_possession(possessions, team, r):
#     if (r['home_team'] == team) & (not pd.isna(r['homepos'])):
#         possessions.append(r['homepos'])
#     elif (r['away_team'] == team) & (not pd.isna(r['awaypos'])):
#         possessions.append(r['awaypos'])
#
#
# def get_last_match_possession(X, teams):
#     df = X.copy()
#     try:
#         for team in teams:
#             mask_team_matches = (df['home_team'] == team) | (df['away_team'] == team)
#             matches = df.loc[mask_team_matches]
#             matches = matches.sort_values(by='date')
#
#             for index, row in matches.iterrows():
#                 previous_match_possession = row['homepos'] if team == row['home_team'] else row['awaypos']
#                 last_match = matches.loc[matches['match_api_id'].shift(1) == row['match_api_id']].dropna(how='all')
#
#                 if not last_match.empty:
#                     if team == last_match['home_team'].values:
#                         df.loc[df['match_api_id'] == last_match['match_api_id'].values[0],
#                                'last_match_possession_home'] = previous_match_possession
#                     else:
#                         df.loc[df['match_api_id'] == last_match['match_api_id'].values[0],
#                                'last_match_possession_away'] = previous_match_possession
#
#         df['last_match_possession_away'] = df['last_match_possession_away'].fillna(
#             df.groupby(['away_team'])['last_match_possession_away'].transform('mean'))
#         df['last_match_possession_home'] = df['last_match_possession_home'].fillna(
#             df.groupby(['home_team'])['last_match_possession_home'].transform('mean'))
#
#         df['last_match_possession_away'] = df['last_match_possession_away'].fillna(
#             df.groupby(['league_name'])['last_match_possession_away'].transform('mean'))
#         df['last_match_possession_home'] = df['last_match_possession_home'].fillna(
#             df.groupby(['league_name'])['last_match_possession_home'].transform('mean'))
#
#         df.last_match_possession_home = df.last_match_possession_home.astype(int)
#         df.last_match_possession_away = df.last_match_possession_away.astype(int)
#         return df
#     except Exception:
#         traceback.print_exc()
#         print('An error occurred')
#
#
def count_days_since_last_match(X, teams):
    df = X.copy()
    try:
        for team in teams:
            mask_team_matches = (df['home_team'] == team) | (df['away_team'] == team)
            matches = df.loc[mask_team_matches]
            matches = matches.sort_values(by='date')

            for index, row in matches.iterrows():
                match_date = row['date']
                next_match = matches.loc[matches['match_api_id'].shift(1) == row['match_api_id']].dropna(how='all')

                if not next_match.empty:
                    days_last_match = next_match['date'].iloc[0] - match_date

                    if team == next_match.iloc[0]['home_team']:
                        df.loc[
                            df['match_api_id'] == next_match['match_api_id'].values[
                                0], 'days_since_lmh'] = days_last_match.days
                    else:
                        df.loc[df['match_api_id'] == next_match['match_api_id'].values[
                            0], 'days_since_lma'] = days_last_match.days

        df['days_since_lmh'] = df['days_since_lmh'].fillna(
            df.groupby(['league_name'])['days_since_lmh'].transform('mean').astype(int))

        df['days_since_lma'] = df['days_since_lma'].fillna(
            df.groupby(['league_name'])['days_since_lma'].transform('mean').astype(int))

        df.days_since_lma = df.days_since_lma.astype(int)
        df.days_since_lmh = df.days_since_lmh.astype(int)
        return df
    except Exception:
        traceback.print_exc()
        print('An error occurred')
#
#
# def get_last_match_winner(X):
#     try:
#         df = X.copy()
#         for index, row in df.iterrows():
#             home_team = row['home_team']
#             away_team = row['away_team']
#
#             mask_all_matches_between_teams = ((df['home_team'] == home_team) | (df['away_team'] == home_team)) & (
#                     (df['home_team'] == away_team) | (df['away_team'] == away_team))
#             all_matches_between_teams = df.loc[mask_all_matches_between_teams]
#
#             for idx, r in all_matches_between_teams.iterrows():
#                 last_match = all_matches_between_teams.loc[
#                     all_matches_between_teams['match_api_id'].shift(1) == r['match_api_id']].dropna(how='all')
#                 if not last_match.empty:
#                     m_winner = football_utils.get_winner(r)
#                     match_api_id_ = df['match_api_id'] == last_match.iloc[0]['match_api_id']
#                     df.loc[match_api_id_, 'lm_winner'] = m_winner
#         return df
#     except Exception:
#         traceback.print_exc()
#         print('An error occurred')
#
#
# def fill_nan_last_match_winner(X):
#     try:
#         df = X.copy()
#         df_detailed_matches_nan_lm_winner = df.loc[df.lm_winner.isna()]
#
#         for index, row in df_detailed_matches_nan_lm_winner.iterrows():
#             home_team = row['home_team']
#             away_team = row['away_team']
#
#             mask_all_matches_between_teams = ((df['home_team'] == home_team) | (
#                     df['away_team'] == home_team)) & ((df['home_team'] == away_team) | (df['away_team'] == away_team))
#
#             all_matches_between_teams = df.loc[mask_all_matches_between_teams]
#             all_matches_between_teams = all_matches_between_teams.sort_values(by='date')
#
#             lm_winner = all_matches_between_teams.mode()['lm_winner'][0]
#             if pd.isna(lm_winner):
#                 lm_winner = football_utils.get_winner(row)
#             df.loc[df['match_api_id'] == row['match_api_id'], 'lm_winner'] = lm_winner
#
#         df.lm_winner = df.lm_winner.astype('category')
#         return df
#     except Exception:
#         traceback.print_exc()
#         print('An error occurred')
#
#
# def count_average_points_from_n_last_matches(X, teams, n=5):
#     df = X.copy()
#     try:
#         for team in teams:
#             mask_find_team_matches = (df['home_team'] == team) | (df['away_team'] == team)
#             team_matches = df.loc[mask_find_team_matches]
#             team_matches = team_matches.sort_values(by='date')
#
#             for index, row in team_matches.iterrows():
#                 mask = (((df['home_team'] == team) | (df['away_team'] == team)) & (team_matches['date'] < row['date']))
#
#                 point_list = team_matches.loc[mask].iloc[-n:].apply(lambda row: football_utils.get_points(row, team),
#                                                                     axis=1)
#                 avg_points_l_n_m = np.nan
#                 if len(point_list) >= n:
#                     avg_points_l_n_m = point_list.mean()
#
#                 if row['home_team'] == team:
#                     df.loc[df.match_api_id == row.match_api_id, f'avg_points_l{n}m_h'] = avg_points_l_n_m
#                 else:
#                     df.loc[df.match_api_id == row.match_api_id, f'avg_points_l{n}m_a'] = avg_points_l_n_m
#         return df
#     except Exception:
#         traceback.print_exc()
#         print('An error occurred')
#
#
# def fill_nan_average_points(X, X_nan, n=5):
#     df = X.copy()
#     df_nan = X_nan.copy()
#
#     try:
#         for idx, row in df_nan.iterrows():
#             team = ''
#
#             if np.isnan(row[f'avg_points_l{n}m_h']):
#                 team = row.home_team
#                 mask_find_team_matches = (df['home_team'] == team) | (df['away_team'] == team)
#                 team_matches = df.loc[mask_find_team_matches]
#                 team_matches = team_matches.sort_values(by='date')
#                 point_list = team_matches.apply(lambda r: football_utils.get_points(r, team), axis=1).mean()
#                 df.loc[df.match_api_id == row.match_api_id, f'avg_points_l{n}m_h'] = point_list
#
#             if np.isnan(row[f'avg_points_l{n}m_a']):
#                 team = row.away_team
#                 mask_find_team_matches = (df['home_team'] == team) | (df['away_team'] == team)
#                 team_matches = df.loc[mask_find_team_matches]
#                 team_matches = team_matches.sort_values(by='date')
#                 point_list = team_matches.apply(lambda r: football_utils.get_points(r, team), axis=1).mean()
#                 df.loc[df.match_api_id == row.match_api_id, f'avg_points_l{n}m_a'] = point_list
#
#         return df
#     except Exception:
#         traceback.print_exc()
#         print('An error occurred')
#
#
# def count_points(X, teams):
#     df = X.copy()
#     try:
#         for team in teams:
#             mask_find_team_matches = (df['home_team'] == team) | (df['away_team'] == team)
#             team_matches = df.loc[mask_find_team_matches]
#             team_matches = team_matches.sort_values(by='date')
#             seasons_unique = team_matches.season.unique()
#
#             for season in seasons_unique:
#                 season_matches = team_matches.loc[team_matches.season == season]
#                 for index, row in season_matches.iterrows():
#                     mask = (((df['home_team'] == team) | (df['away_team'] == team)) &
#                             (team_matches['date'] < row['date']))
#
#                     point_list = season_matches.loc[mask].apply(lambda row: football_utils.get_points(row, team),
#                                                                 axis=1)
#                     points = 0
#
#                     if len(point_list):
#                         points = point_list.sum()
#
#                     if row['home_team'] == team:
#                         df.loc[
#                             df.match_api_id == row.match_api_id, 'points_home'] = points
#                     else:
#                         df.loc[
#                             df.match_api_id == row.match_api_id, 'points_away'] = points
#
#         df.points_home = df.points_home.astype(int)
#         df.points_away = df.points_away.astype(int)
#         return df
#     except Exception:
#         traceback.print_exc()
#         print('An error occurred')
