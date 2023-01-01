import logging
import sqlite3 as db
from pathlib import PureWindowsPath

import pandas as pd

logger = logging.getLogger(__name__)

ROOT_DIR = PureWindowsPath(__file__).parent.parent.parent  # This is your Project Root
DB_DIR = '/eu_soccer_database'
CHUNK_DIR = '/chunk_data'


def load_and_chunk_data():
    db_path = r"{ROOT_DIR}/{DB_DIR}/database.sqlite".format(ROOT_DIR=ROOT_DIR, DB_DIR=DB_DIR).replace('\\', '/')
    conn = db.connect(db_path)
    chunk_size = 5000
    batch_no = 1
    for chunk in pd.read_sql("SELECT m.match_api_id,"
                             " Country.name AS country_name,"
                             " League.name AS league_name,"
                             " season,"
                             " stage,"
                             " m.date,"
                             " AT.team_long_name AS away_team,"
                             " HT.team_long_name AS home_team,"
                             " home_team_goal,"
                             " away_team_goal,"
                             " m.possession,"
                             " CASE"
                             " WHEN m.home_team_goal > m.away_team_goal THEN 'H'"
                             " WHEN m.home_team_goal < m.away_team_goal THEN 'A'"
                             " WHEN m.home_team_goal = m.away_team_goal THEN 'D'"
                             " END AS result_match,"
                             " H1.player_api_id as home_player_1,"
                             " H2.player_api_id as home_player_2,"
                             " H3.player_api_id as home_player_3,"
                             " H4.player_api_id as home_player_4,"
                             " H5.player_api_id as home_player_5,"
                             " H6.player_api_id as home_player_6,"
                             " H7.player_api_id as home_player_7,"
                             " H8.player_api_id as home_player_8,"
                             " H9.player_api_id as home_player_9,"
                             " H10.player_api_id as home_player_10,"
                             " H11.player_api_id as home_player_11,"
                             " A1.player_api_id as away_player_1,"
                             " A2.player_api_id as away_player_2,"
                             " A3.player_api_id as away_player_3,"
                             " A4.player_api_id as away_player_4,"
                             " A5.player_api_id as away_player_5,"
                             " A6.player_api_id as away_player_6,"
                             " A7.player_api_id as away_player_7,"
                             " A8.player_api_id as away_player_8,"
                             " A9.player_api_id as away_player_9,"
                             " A10.player_api_id as away_player_10,"
                             " A11.player_api_id as away_player_11, "
                             " m.B365H,"
                             " m.B365D,"
                             " m.B365A,"
                             " m.BWH,"
                             " m.BWD,"
                             " m.BWA,"
                             " m.IWH,"
                             " m.IWD,"
                             " m.IWA,"
                             " m.LBH,"
                             " m.LBD,"
                             " m.LBA,"
                             " m.PSH,"
                             " m.PSD,"
                             " m.PSA,"
                             " m.WHH,"
                             " m.WHD,"
                             " m.WHA"
                             " FROM Match as m"
                             " JOIN Country on Country.id = m.country_id"
                             " JOIN League on League.id = m.league_id"
                             " LEFT JOIN Team AS HT on HT.team_api_id = m.home_team_api_id"
                             " LEFT JOIN Team AS AT on AT.team_api_id = m.away_team_api_id"
                             " LEFT JOIN Player AS H1 on H1.player_api_id = m.home_player_6"
                             " LEFT JOIN Player AS H2 on H2.player_api_id = m.home_player_6"
                             " LEFT JOIN Player AS H3 on H3.player_api_id = m.home_player_6"
                             " LEFT JOIN Player AS H4 on H4.player_api_id = m.home_player_6"
                             " LEFT JOIN Player AS H5 on H5.player_api_id = m.home_player_6"
                             " LEFT JOIN Player AS H6 on H6.player_api_id = m.home_player_6"
                             " LEFT JOIN Player AS H7 on H7.player_api_id = m.home_player_7"
                             " LEFT JOIN Player AS H8 on H8.player_api_id = m.home_player_8"
                             " LEFT JOIN Player AS H9 on H9.player_api_id = m.home_player_9"
                             " LEFT JOIN Player AS H10 on H10.player_api_id = m.home_player_10"
                             " LEFT JOIN Player AS H11 on H11.player_api_id = m.home_player_11"
                             " LEFT JOIN Player AS A1 on A1.player_api_id = m.away_player_6"
                             " LEFT JOIN Player AS A2 on A2.player_api_id = m.away_player_6"
                             " LEFT JOIN Player AS A3 on A3.player_api_id = m.away_player_6"
                             " LEFT JOIN Player AS A4 on A4.player_api_id = m.away_player_6"
                             " LEFT JOIN Player AS A5 on A5.player_api_id = m.away_player_6"
                             " LEFT JOIN Player AS A6 on A6.player_api_id = m.away_player_6"
                             " LEFT JOIN Player AS A7 on A7.player_api_id = m.away_player_7"
                             " LEFT JOIN Player AS A8 on A8.player_api_id = m.away_player_8"
                             " LEFT JOIN Player AS A9 on A9.player_api_id = m.away_player_9"
                             " LEFT JOIN Player AS A10 on A10.player_api_id = m.away_player_10"
                             " LEFT JOIN Player AS A11 on A11.player_api_id = m.away_player_11"
                             " WHERE League.id IN (1729, 4769, 7809, 10257, 21518)"
                             " AND m.possession IS NOT NULL"
                             " ORDER by date;", conn, chunksize=chunk_size):
        chunk_path = r"{ROOT_DIR}{CHUNK_DIR}/".format(ROOT_DIR=ROOT_DIR, CHUNK_DIR=CHUNK_DIR).replace('\\', '/')
        chunk.to_csv(chunk_path + 'chunk_' + str(batch_no) + '.csv', index=False)
        logger.info(f'Number of chunks: {batch_no}')
        batch_no += 1


def load_player_stats_data():
    db_path = r"{ROOT_DIR}/{DB_DIR}/database.sqlite".format(ROOT_DIR=ROOT_DIR, DB_DIR=DB_DIR).replace('\\', '/')
    conn = db.connect(db_path)

    return pd.read_sql("SELECT pa.player_api_id,"
                       " pa.date,"
                       " pa.overall_rating"
                       " FROM Player_Attributes as pa;", conn)
