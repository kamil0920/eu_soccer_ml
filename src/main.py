import logging
import logging.config
import os
from datetime import datetime

import pandas as pd
from dotenv import find_dotenv, load_dotenv
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

# find .env file in parent directory
env_file = find_dotenv()
load_dotenv()

CONFIG_DIR = "/config"
LOG_DIR = "/logs"

def setup_logging():
    """Load logging configuration"""
    log_configs = {"dev": "logging.dev.ini", "prod": "logging.prod.ini"}
    config = log_configs.get(os.environ["ENV"], "logging.dev.ini")
    config_path = "/".join([CONFIG_DIR, config])

    timestamp = datetime.now().strftime("%Y%m%d-%H:%M:%S")

    logging.config.fileConfig(
        config_path,
        disable_existing_loggers=False,
        defaults={"logfilename": f"{LOG_DIR}/{timestamp}.log"}
    )


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Program started")

    logger.info("Chunk data to files.")
    football_repoistory.load_and_chunk_data()

    logger.info("Load first chunk data.")
    df_detailed_matches = pd.read_csv('chunk_data/chunk1.csv')

    logger.info("Profile data.")
    profile = ProfileReport(df_detailed_matches, title='Detailed matches', minimal=True)
    profile.to_file(output_file="report/first_profile.html")

    logger.info("--->Start preprocess data.<---")
    df_detailed_matches['date'] = pd.to_datetime(df_detailed_matches['date']).dt.date
    df_detailed_matches[
        ['country_name', 'league_name', 'season', 'home_team', 'away_team', 'result_match', 'possession']] = \
        df_detailed_matches[
            ['country_name', 'league_name', 'season', 'home_team', 'away_team', 'result_match', 'possession']].astype(
            'category')

    df_detailed_matches = df_detailed_matches.drop(['PSH', 'PSD', 'PSA'], axis=1)

    logger.info("Retrieve all unique teams.")
    teams = pd.unique(df_detailed_matches[['home_team', 'away_team']].values.ravel('K'))

    logger.info("Count how many goals team get in last match.")
    df_detailed_matches = goals_preprocess_feature.count_last_match_goals(df_detailed_matches, teams)
    df_detailed_matches = football_utils.fill_nan_goals(df_detailed_matches, 'lm_goals_home', 'lm_goals_away')

    logger.info("Count average goals team get in last n matches.")
    df_detailed_matches = goals_preprocess_feature.count_average_goals_from_last_n_matches(df_detailed_matches, teams)
    df_detailed_matches = football_utils.fill_nan_goals(df_detailed_matches, 'avg_l5m_h', 'avg_l5m_hh')
    df_detailed_matches = football_utils.fill_nan_goals(df_detailed_matches, 'avg_l5m_a', 'avg_l5m_aa')

    logger.info("Count streak wins or lose in last matches.")
    df_detailed_matches = streaks_preprocess_feature.count_streak_wins(df_detailed_matches, teams)
    df_detailed_matches = streaks_preprocess_feature.count_streak_lose(df_detailed_matches, teams)

    logger.info("Process xml column, get team possession in last match.")
    df_detailed_matches = possession_preprocess_feature.xml_to_feature_possession(df_detailed_matches)
    df_detailed_matches_nan_possession = df_detailed_matches.loc[
        (df_detailed_matches['awaypos'].isna()) | (df_detailed_matches['homepos'].isna())]
    df_detailed_matches = possession_preprocess_feature.fill_nan_possession(df_detailed_matches,
                                                                            df_detailed_matches_nan_possession)
    df_detailed_matches = possession_preprocess_feature.get_last_match_possession(df_detailed_matches, teams)
    df_detailed_matches = df_detailed_matches.drop(['homepos', 'awaypos'], axis=1)

    logger.info("Count days since last match.")
    df_detailed_matches = football_preprocess_features.count_days_since_last_match(df_detailed_matches, teams)

    logger.info("Get last match winner between teams.")
    df_detailed_matches = lm_winner_preprocess_feature.get_last_match_winner(df_detailed_matches)
    df_detailed_matches = lm_winner_preprocess_feature.fill_nan_last_match_winner(df_detailed_matches)

    logger.info("Count team points.")
    df_detailed_matches = points_preprocess_feature.count_points(df_detailed_matches, teams)

    logger.info("Count team average points from n last matches.")
    df_detailed_matches = points_preprocess_feature.count_average_points_from_n_last_matches(df_detailed_matches, teams)
    df_avg_goals_nan = df_detailed_matches.loc[
        (df_detailed_matches['avg_points_l5m_h'].isna()) | (df_detailed_matches['avg_points_l5m_a'].isna())]
    df_detailed_matches = points_preprocess_feature.fill_nan_average_points(df_detailed_matches, df_avg_goals_nan)

    logger.info("Filling in missing bets data.")
    df_detailed_matches = bets_preprocess_feature.fill_nan_bets(df_detailed_matches)

    logger.info("--->End preprocess data.<---")

    X = df_detailed_matches.drop(axis=1, columns=['home_team_goal', 'away_team_goal', 'possession', 'result_match', ])
    y = df_detailed_matches.drop('result_match', axis=1)

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

    print(f'X_train shape {X_train.shape}')
    print(f'y_train shape {y_train.shape}')
    print(f'X_test shape {X_test.shape}')
    print(f'y_test shape {y_test.shape}')
    print(f'\nTest ratio: {len(X_test) / len(X):.2f}')
    print(f'\ny_train:\n{y_train.value_counts()}')
    print(f'\ny_test:\n{y_test.value_counts()}')

    logger.info("Program finished")
