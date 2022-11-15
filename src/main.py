import logging
import logging.config
import os
from datetime import datetime
from pathlib import PureWindowsPath

import pandas as pd
from pandas_profiling import ProfileReport
from sklearn.model_selection import train_test_split

from data_processing import bets_preprocess_feature
from data_processing import football_preprocess_features
from data_processing import football_repoistory
from data_processing import football_utils
from data_processing import goals_preprocess_feature
from data_processing import lm_winner_preprocess_feature
from data_processing import points_preprocess_feature
from data_processing import possession_preprocess_feature
from data_processing import streaks_preprocess_feature

ROOT_DIR = PureWindowsPath(__file__).parent.parent
CONFIG_DIR = "/config"
LOG_DIR = "/logs"
CHUNK_DIR = '/chunk_data'
REPORT_DIR = '/report'

N_LAST_MATCHES = 5


def setup_logging():
    """Load logging configuration"""
    log_configs = {"dev": "logging.dev.ini", "prod": "logging.prod.ini"}
    config = log_configs.get(os.environ["ENV"], "logging.dev.ini")
    config_path = "\\".join([str(ROOT_DIR), CONFIG_DIR, config])

    timestamp = datetime.now().strftime('%m_%d_%Y_%H_%M_%S')
    log_file_path = r"{ROOT_DIR}{LOG_DIR}/{timestamp}.log".format(ROOT_DIR=ROOT_DIR, LOG_DIR=LOG_DIR, timestamp=str(timestamp)).replace('\\', '/')

    logging.config.fileConfig(
        config_path,
        disable_existing_loggers=False,
        defaults={"logfilename": log_file_path}
    )


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Program started")

    logger.info("Chunk data to files.")
    football_repoistory.load_and_chunk_data()

    logger.info("Load first chunk data.")
    chunk_file_path = r"{ROOT_DIR}{CHUNK_DIR}/chunk_1.csv".format(ROOT_DIR=ROOT_DIR, CHUNK_DIR=CHUNK_DIR).replace('\\', '/')
    df_detailed_matches = pd.read_csv(chunk_file_path)

    logger.info("Profile data.")
    report_file_path = r"{ROOT_DIR}{REPORT_DIR}/first_report.csv".format(ROOT_DIR=ROOT_DIR, REPORT_DIR=REPORT_DIR).replace('\\', '/')
    profile = ProfileReport(df_detailed_matches, title='Detailed matches', minimal=True)
    profile.to_file(output_file=report_file_path)

    logger.info("--->Start preprocess data.<---")
    df_detailed_matches['date'] = pd.to_datetime(df_detailed_matches['date']).dt.date
    df_detailed_matches[
        ['country_name', 'league_name', 'season', 'home_team', 'away_team', 'result_match', 'possession']] = \
        df_detailed_matches[
            ['country_name', 'league_name', 'season', 'home_team', 'away_team', 'result_match', 'possession']].astype(
            'category')

    df_detailed_matches = df_detailed_matches.drop(['PSH', 'PSD', 'PSA'], axis=1)

    logger.debug("Retrieve all unique teams.")
    teams = pd.unique(df_detailed_matches[['home_team', 'away_team']].values.ravel('K'))

    logger.debug("Count how many goals team get in last match.")
    df_detailed_matches = goals_preprocess_feature.count_last_match_goals(df_detailed_matches, teams)
    df_detailed_matches = football_utils.fill_nan_goals(df_detailed_matches, 'lm_goals_home', 'lm_goals_away')

    logger.debug("Count average goals team get in last n matches.")
    df_detailed_matches = goals_preprocess_feature.count_average_goals_from_last_n_matches(df_detailed_matches, teams, n=N_LAST_MATCHES)
    df_detailed_matches = football_utils.fill_nan_goals(df_detailed_matches, f'avg_l{N_LAST_MATCHES}m_h', f'avg_l{N_LAST_MATCHES}m_hh')
    df_detailed_matches = football_utils.fill_nan_goals(df_detailed_matches, f'avg_l{N_LAST_MATCHES}m_a', f'avg_l{N_LAST_MATCHES}m_aa')

    logger.debug("Count streak wins or lose in last matches.")
    df_detailed_matches = streaks_preprocess_feature.count_streak_wins(df_detailed_matches, teams)
    df_detailed_matches = streaks_preprocess_feature.count_streak_lose(df_detailed_matches, teams)

    logger.debug("Process xml column, get team possession in last match.")
    df_detailed_matches = possession_preprocess_feature.xml_to_feature_possession(df_detailed_matches)
    df_detailed_matches_nan_possession = df_detailed_matches.loc[
        (df_detailed_matches['awaypos'].isna()) | (df_detailed_matches['homepos'].isna())]
    df_detailed_matches = possession_preprocess_feature.fill_nan_possession(df_detailed_matches,
                                                                            df_detailed_matches_nan_possession)
    df_detailed_matches = possession_preprocess_feature.get_last_match_possession(df_detailed_matches, teams)
    df_detailed_matches = df_detailed_matches.drop(['homepos', 'awaypos'], axis=1)

    logger.debug("Count days since last match.")
    df_detailed_matches = football_preprocess_features.count_days_since_last_match(df_detailed_matches, teams)

    logger.debug("Get last match winner between teams.")
    df_detailed_matches = lm_winner_preprocess_feature.get_last_match_winner(df_detailed_matches)
    df_detailed_matches = lm_winner_preprocess_feature.fill_nan_last_match_winner(df_detailed_matches)

    logger.debug("Count team points.")
    df_detailed_matches = points_preprocess_feature.count_points(df_detailed_matches, teams)

    logger.debug("Count team average points from n last matches.")
    df_detailed_matches = points_preprocess_feature.count_average_points_from_n_last_matches(df_detailed_matches, teams, n=N_LAST_MATCHES)
    df_avg_goals_nan = df_detailed_matches.loc[
        (df_detailed_matches[f'avg_points_l{N_LAST_MATCHES}m_h'].isna()) | (df_detailed_matches[f'avg_points_l{N_LAST_MATCHES}m_a'].isna())]
    df_detailed_matches = points_preprocess_feature.fill_nan_average_points(df_detailed_matches, df_avg_goals_nan)

    logger.debug("Filling in missing bets data.")
    df_detailed_matches = bets_preprocess_feature.fill_nan_bets(df_detailed_matches)

    logger.info("--->End preprocess data.<---")

    logger.info("Split data into train set and test set.")

    X = df_detailed_matches.drop(axis=1, columns=['home_team_goal', 'away_team_goal', 'possession', 'result_match', ])
    y = df_detailed_matches['result_match']

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

    print(f'X_train shape {X_train.shape}')
    print(f'y_train shape {y_train.shape}')
    print(f'X_test shape {X_test.shape}')
    print(f'y_test shape {y_test.shape}')
    print(f'\nTest ratio: {len(X_test) / len(X):.2f}')
    print(f'\ny_train:\n{y_train.value_counts()}')
    print(f'\ny_test:\n{y_test.value_counts()}')

    logger.info("Program finished")
