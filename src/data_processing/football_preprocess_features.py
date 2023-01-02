import logging
import traceback

logger = logging.getLogger(__name__)


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

        return df.loc[(df.days_since_lma < 50) & (df.days_since_lmh < 50)]
    except Exception:
        traceback.print_exc()
        print('An error occurred')