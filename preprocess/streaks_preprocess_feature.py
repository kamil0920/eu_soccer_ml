import traceback


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
    except Exception:
        traceback.print_exc()
        print('An error occurred')


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
    except Exception:
        traceback.print_exc()
        print('An error occurred')
