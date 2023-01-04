import logging
import traceback

import numpy as np
import pandas as pd

from src.data_processing import football_utils

logger = logging.getLogger(__name__)


def count_average_points_from_n_last_matches(X, teams, n=5):
    df = X.copy()
    try:
        for team in teams:
            mask_find_team_matches = (df['home_team'].eq(team)) | (df['away_team'].eq(team))
            team_matches = df.loc[mask_find_team_matches]
            team_matches = team_matches.sort_values(by='date')

            for index, row in team_matches.iterrows():
                mask = (((df['home_team'].eq(team)) | (df['away_team'].eq(team))) & (team_matches['date'].le(row['date'])))

                point_list = team_matches.loc[mask].iloc[-n:].apply(lambda row: football_utils.get_points(row, team),
                                                                    axis=1)
                avg_points_l_n_m = np.nan
                if len(point_list) >= n:
                    avg_points_l_n_m = point_list.mean()

                if row['home_team'] == team:
                    df.loc[df.match_api_id.eq(row.match_api_id), f'avg_points_l{n}m_h'] = avg_points_l_n_m
                else:
                    df.loc[df.match_api_id.eq(row.match_api_id), f'avg_points_l{n}m_a'] = avg_points_l_n_m
        return df
    except Exception:
        traceback.print_exc()
        print('An error occurred')


def fill_nan_average_points(X, X_nan, n=5):
    df = X.copy()
    df_nan = X_nan.copy()

    try:
        for idx, row in df_nan.iterrows():
            team = ''

            if np.isnan(row[f'avg_points_l{n}m_h']):
                team = row.home_team
                mask_find_team_matches = (df['home_team'] == team) | (df['away_team'] == team)
                team_matches = df.loc[mask_find_team_matches]
                team_matches = team_matches.sort_values(by='date')
                point_list = team_matches.apply(lambda r: football_utils.get_points(r, team), axis=1).mean()
                df.loc[df.match_api_id == row.match_api_id, f'avg_points_l{n}m_h'] = point_list

            if np.isnan(row[f'avg_points_l{n}m_a']):
                team = row.away_team
                mask_find_team_matches = (df['home_team'] == team) | (df['away_team'] == team)
                team_matches = df.loc[mask_find_team_matches]
                team_matches = team_matches.sort_values(by='date')
                point_list = team_matches.apply(lambda r: football_utils.get_points(r, team), axis=1).mean()
                df.loc[df.match_api_id == row.match_api_id, f'avg_points_l{n}m_a'] = point_list

        return df
    except Exception:
        traceback.print_exc()
        print('An error occurred')


def count_points(X, teams):
    df = X.copy()
    try:
        for team in teams:
            mask_find_team_matches = (df['home_team'].eq(team)) | (df['away_team'].eq(team))
            team_matches = df.loc[mask_find_team_matches]
            team_matches = team_matches.sort_values(by='date')
            seasons_unique = team_matches.season.unique()

            for season in seasons_unique:
                season_matches = team_matches.loc[team_matches.season == season]
                for index, row in season_matches.iterrows():
                    mask = (((df['home_team'].eq(team)) | (df['away_team'].eq(team))) &
                            (team_matches['date'] < row['date']))

                    point_list = season_matches.loc[mask].apply(lambda row: football_utils.get_points(row, team),
                                                                axis=1)
                    points = 0

                    if len(point_list):
                        points = point_list.sum()

                    if row['home_team'] == team:
                        df.loc[
                            df.match_api_id.eq(row.match_api_id), 'points_home'] = points
                    else:
                        df.loc[
                            df.match_api_id.eq(row.match_api_id), 'points_away'] = points

        df.points_home = df.points_home.astype(int)
        df.points_away = df.points_away.astype(int)
        return df
    except Exception:
        traceback.print_exc()
        print('An error occurred')


def aggregate_result_match_points(X, colH, colA):
    new_df = pd.DataFrame(columns=['type', 'good_points', 'wrong_points'])
    df_ = X.copy()

    df_['points_vs_result'] = X[[colH, colA, 'result_match']].apply(
        lambda x: check_bets_with_win_probability(x, colH, colA), axis=1)

    df_group = df_.groupby(by=['result_match', 'points_vs_result'], )['points_vs_result'].count()
    uniques = df_group.index.get_level_values(0).unique()

    for i in list(uniques):
        df_single = df_group.get(i)
        dict_ = {
            'type': i,
            'good_points': df_single[0],
            'wrong_points': df_single[1]
        }
        frame = pd.DataFrame(dict_, index=[0])
        new_df = pd.concat([new_df, frame])
    return new_df


def check_bets_with_win_probability(X, colH, colA):
    # print(f'colH: {X.get(colH)}\ncolA: {X.get(colA)}\n')
    if ((X.get(colH) > X.get(colA)) & (X.get('result_match') == 'H')) | \
            ((X.get(colH) < X.get(colA)) & (X.get('result_match') == 'A')) | \
            ((X.get(colH) == X.get(colA)) & (X.get('result_match') == 'D')):
        return True
    else:
        return False


# df_.loc[df_.match_api_id == 489057, ['B365H', 'B365D', 'B365A', 'points_home', 'points_away', 'home_team_goal', 'away_team_goal', 'points_vs_book_bet', 'result_match']]

# def aggregate_result_match_points(X, colH, colA, betH, betD, betA):
#     new_df = pd.DataFrame(columns=['type', 'good_points', 'wrong_points'])
#     df_ = X.copy()
#
#     df_['points_vs_book_bet'] = X[[colH, colA, betH, betD, betA, 'result_match']].apply(
#         lambda x: check_bets_with_win_probability(x, colH, colA, betH, betD, betA), axis=1)
#
#     df_group = df_.groupby(by=['result_match', 'points_vs_book_bet'], )['points_vs_book_bet'].count()
#     uniques = df_group.index.get_level_values(0).unique()
#
#     for i in list(uniques):
#         df_single = df_group.get(i)
#         dict_ = {
#             'type': i,
#             'good_points': df_single[0],
#             'wrong_points': df_single[1]
#         }
#         frame = pd.DataFrame(dict_, index=[0])
#         new_df = pd.concat([new_df, frame])
#     return new_df
#
#
# def check_bets_with_win_probability(X, colH, colA, betH, betD, betA):
#     # print(f'colH: {X.get(colH)}\ncolA: {X.get(colA)}\n')
#     book_bet = X.loc[[betH, betD, betA]].astype('float').idxmin()
#
#     if ((X.get(colH) > X.get(colA)) & ('H' in book_bet)) | \
#             ((X.get(colH) < X.get(colA)) & ('A' in book_bet)) | \
#             ((X.get(colH) == X.get(colA)) & ('D' in book_bet)):
#         return True
#     else:
#         return False