import logging
import sqlite3 as db
from pathlib import PureWindowsPath

import pandas as pd

logger = logging.getLogger(__name__)

ROOT_DIR = PureWindowsPath(__file__).parent.parent.parent # This is your Project Root
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
                             " HT.team_long_name AS  home_team,"
                             " AT.team_long_name AS away_team,"
                             " home_team_goal,"
                             " away_team_goal,"
                             " m.possession,"
                             " CASE"
                             " WHEN m.home_team_goal > m.away_team_goal THEN 'H'"
                             " WHEN m.home_team_goal < m.away_team_goal THEN 'A'"
                             " WHEN m.home_team_goal = m.away_team_goal THEN 'D'"
                             " END AS result_match,"
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
                             " WHERE League.id IN (1729, 4769, 7809, 10257, 21518)"
                             " AND m.possession IS NOT NULL"
                             " ORDER by date;", conn, chunksize=chunk_size):

        chunk_path = r"{ROOT_DIR}{CHUNK_DIR}/".format(ROOT_DIR=ROOT_DIR, CHUNK_DIR=CHUNK_DIR).replace('\\', '/')
        chunk.to_csv(chunk_path + 'chunk_' + str(batch_no) + '.csv', index=False)
        logger.info(f'Number of chunks: {batch_no}')
        batch_no += 1
