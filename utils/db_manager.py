import sqlite3
import os


def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")

    conn = sqlite3.connect("data/predictions.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS predictions
              (user_id INTEGER, match_url TEXT, my_pick TEXT, opponent TEXT,
                PRIMARY KEY (user_id, match_url))"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS history
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  match_name TEXT,
                  predicted_team TEXT,
                  winner_team TEXT,
                  is_correct INTEGER,
                  date TEXT)"""
    )
    conn.commit()
    conn.close()


def save_prediction(user_id, match_url, team_name, opponent_name):
    conn = sqlite3.connect("data/predictions.db")
    c = conn.cursor()
    # すでに同じ試合に予想してたら上書き、なければ新規保存
    c.execute(
        "INSERT OR REPLACE INTO predictions VALUES (?, ?, ?, ?)",
        (user_id, match_url, team_name, opponent_name),
    )
    conn.commit()
    conn.close()


def add_to_history(user_id, match_name, predicted, winner, is_correct):
    import datetime

    conn = sqlite3.connect("data/predictions.db")
    c = conn.cursor()
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        """INSERT INTO history (user_id, match_name, predicted_team, winner_team, is_correct, date)
                  VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, match_name, predicted, winner, is_correct, date_str),
    )
    conn.commit()
    conn.close()
