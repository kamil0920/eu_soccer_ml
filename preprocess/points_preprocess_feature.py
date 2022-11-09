import traceback

import numpy as np

from preprocess import football_utils


def count_average_points_from_n_last_matches(X, teams, n=5):
    df = X.copy()
    try:
        for team in teams:
            mask_find_team_matches = (df['home_team'] == team) | (df['away_team'] == team)
            team_matches = df.loc[mask_find_team_matches]
            team_matches = team_matches.sort_values(by='date')

            for index, row in team_matches.iterrows():
                mask = (((df['home_team'] == team) | (df['away_team'] == team)) & (team_matches['date'] < row['date']))

                point_list = team_matches.loc[mask].iloc[-n:].apply(lambda row: football_utils.get_points(row, team),
                                                                    axis=1)
                avg_points_l_n_m = np.nan
                if len(point_list) >= n:
                    avg_points_l_n_m = point_list.mean()

                if row['home_team'] == team:
                    df.loc[df.match_api_id == row.match_api_id, f'avg_points_l{n}m_h'] = avg_points_l_n_m
                else:
                    df.loc[df.match_api_id == row.match_api_id, f'avg_points_l{n}m_a'] = avg_points_l_n_m
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
            mask_find_team_matches = (df['home_team'] == team) | (df['away_team'] == team)
            team_matches = df.loc[mask_find_team_matches]
            team_matches = team_matches.sort_values(by='date')
            seasons_unique = team_matches.season.unique()

            for season in seasons_unique:
                season_matches = team_matches.loc[team_matches.season == season]
                for index, row in season_matches.iterrows():
                    mask = (((df['home_team'] == team) | (df['away_team'] == team)) &
                            (team_matches['date'] < row['date']))

                    point_list = season_matches.loc[mask].apply(lambda row: football_utils.get_points(row, team),
                                                                axis=1)
                    points = 0

                    if len(point_list):
                        points = point_list.sum()

                    if row['home_team'] == team:
                        df.loc[
                            df.match_api_id == row.match_api_id, 'points_home'] = points
                    else:
                        df.loc[
                            df.match_api_id == row.match_api_id, 'points_away'] = points

        df.points_home = df.points_home.astype(int)
        df.points_away = df.points_away.astype(int)
        return df
    except Exception:
        traceback.print_exc()
        print('An error occurred')