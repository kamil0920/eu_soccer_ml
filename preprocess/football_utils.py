import pandas as pd
import xml.etree.cElementTree as et

import pandas as pd

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
logging.debug("test")

def process_xml_columns(df_new_cols, cols, match, xml_col):
    path = match[xml_col]
    if path is not None:
        root = et.fromstring(path)
        try:
            temp_column_list = []
            for column in cols:
                row_elements = root.findall('.//{}'.format(column))
                row_list = []
                for row in row_elements:
                    row_list.append(row.text)
                temp_column_list.append(row_list)
            df = pd.DataFrame(temp_column_list)
            df = df.transpose()
            df.columns = df_new_cols
            df['match_api_id'] = match.match_api_id
            return df
        except Exception as e:
            print(e)

def create_new_df_from_xml(df, xml_column, df_cols, df_new_cols):
    new_df = pd.DataFrame()
    for index, row in df[df[xml_column].notna()].iterrows():
        df = process_xml_columns(df_new_cols, df_cols, row, xml_column)
        new_df = pd.concat([new_df, df], ignore_index=True)
    return new_df


def fill_nan_goals(df, col1, col2):
    df_col1_nan = df.loc[df[col1].isna()]
    df_col2_nan = df.loc[df[col2].isna()]
    for index, row in df_col1_nan.iterrows():
        avg_mean = df.loc[df.home_team == row.home_team][col1].mean()
        if avg_mean == avg_mean:
            df.loc[df.match_api_id == row.match_api_id, col1] = round(avg_mean)
        else:
            df.loc[df.match_api_id == row.match_api_id, col1] = 0
    for index, row in df_col2_nan.iterrows():
        avg_mean = df.loc[df.away_team == row.away_team][col2].mean()
        if avg_mean == avg_mean:
            df.loc[df.match_api_id == row.match_api_id, col2] = round(avg_mean)
        else:
            df.loc[df.match_api_id == row.match_api_id, col1] = 0
    return df


def missing_values(df):
    percent_missing = df.isnull().sum() * 100 / len(df)
    missing_value_df = pd.DataFrame({'column_name': df.columns,
                                     'percent_missing': percent_missing})
    return missing_value_df


def get_winner(row):
    if row['result_match'] == 'H':
        m_winner = row['home_team']
    elif row['home_team_goal'] == 'D':
        m_winner = 'Draw'
    else:
        m_winner = row['away_team']
    return m_winner


def get_points(row, team):
    if row['home_team'] == team:
        if row['result_match'] == 'H':
            return 3
        elif row['result_match'] == 'A':
            return 0
        else:
            return 1
    else:
        if row['home_team_goal'] == 'H':
            return 0
        elif row['home_team_goal'] == 'A':
            return 3
        else:
            return 1

from sklearn.feature_selection import SelectKBest


# for chi-squared feature selection
def select_KBest(X, y, criteria, k):
    selector = SelectKBest(criteria, k=k)
    selector.fit_transform(X,y)
    X = X[[val for i,val in enumerate(X.columns) if selector.get_support()[i]]]
    return X

# create home_winner
def preprocess_category_string(category_row):
    if category_row == 'H':
        return 'yes'
    else:
        return 'no'

def preprocess_if_bet_placed_well(X, colH, colD, colA):
    # print(f'B365H: {X.colH}, colD: {X.B365D}, colA: {X.B365A}, result: {X.result_match} ')
    if (X.get(colH) < X.get(colA)) & (X.get('result_match') == 'H'):
        return True
    elif (X.get(colH) > X.get(colA)) & (X.get('result_match') == 'A'):
        return True
    elif ((X.get(colD) < X.get(colA)) & (X.get(colD) < X.get(colH))) & (X.get('result_match') == 'D'):
        return True
    else:
        return False

def get_result_name(short_name):
    if short_name == 'H':
        return 'home tem win.'
    elif short_name == 'D':
        return 'draw.'
    else:
        return 'away team win.'


def get_bookmaker_type(short_name):
    return [short_name[:-1], short_name[-1]]

def aggregate_bookmarks_bets(X, colH, colD, colA):
    new_df = pd.DataFrame(columns=['bookmaker', 'type', 'good_bet', 'wrong_bet'])
    df_ = X.copy()

    df_['bet_vs_result'] = X[[colH, colD, colA, 'result_match']].apply(lambda x: preprocess_if_bet_placed_well(x, colH, colD, colA), axis=1)

    logger.debug(f"len new col: {df_['bet_vs_result'].value_counts()}")

    df_group = df_.groupby(by=['result_match', 'bet_vs_result'], )['bet_vs_result'].count()
    uniques = df_group.index.get_level_values(0).unique()

    for i in list(uniques):
        df_single = df_group.get(i)
        dict_ = {
            'bookmaker': get_bookmaker_type(colH)[0],
            'type': get_bookmaker_type(i)[1],
            'good_bet': df_single[0],
            'wrong_bet': df_single[1]
        }
        frame = pd.DataFrame(dict_, index=[0])
        new_df = pd.concat([new_df, frame])
    return new_df

def check_streak_with_win_probability(X, colH, colA):
    # print(f'colH: {X.get(colH)}\ncolA: {X.get(colA)}\n')
    if ((X.get(colH) > X.get(colA)) & (X.get('result_match') == 'H')) |\
            ((X.get(colH) < X.get(colA)) & (X.get('result_match') == 'A')) |\
            ((X.get(colH) == X.get(colA)) & (X.get('result_match') == 'D')):
        return True
    else:
        return False

def aggregate_streaks(X, colH, colA):
    new_df = pd.DataFrame(columns=[ 'type', 'good_streak', 'wrong_streak'])
    df_ = X.copy()

    df_['streak_vs_result'] = X[[colH, colA, 'result_match']].apply(lambda x: check_streak_with_win_probability(x, colH, colA), axis=1)

    logger.debug(f"len new col: {df_['streak_vs_result'].value_counts()}")

    df_group = df_.groupby(by=['result_match', 'streak_vs_result'], )['streak_vs_result'].count()
    uniques = df_group.index.get_level_values(0).unique()

    for i in list(uniques):
        df_single = df_group.get(i)
        dict_ = {
            'type': i,
            'good_streak': df_single[0],
            'wrong_streak': df_single[1]
        }
        frame = pd.DataFrame(dict_, index=[0])
        new_df = pd.concat([new_df, frame])
    return new_df

