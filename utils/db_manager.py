import sqlite3
import os
import datetime


def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")

    conn = sqlite3.connect("data/predictions.db")
    c = conn.cursor()

    c.execute(
        """CREATE TABLE IF NOT EXISTS predictions
              (user_id INTEGER, match_url TEXT, my_pick TEXT, opponent TEXT,start_time TEXT,
                PRIMARY KEY (user_id, match_url))"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS history
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER, match_name TEXT, predicted_team TEXT,
              winner_team TEXT, is_correct INTEGER, date TEXT)"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS posted_matches 
              (guild_id INTEGER, match_url TEXT, PRIMARY KEY (guild_id, match_url))"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS guild_settings 
              (guild_id INTEGER PRIMARY KEY, channel_id INTEGER)"""
    )

    conn.commit()
    conn.close()


def save_prediction(user_id, match_url, my_pick, opponent, start_time):
    print(
        f"DEBUG: Saving to DB -> user: {user_id}, time: {start_time} (Type: {type(start_time)})"
    )
    conn = sqlite3.connect("data/predictions.db")
    c = conn.cursor()
    c.execute(
        """INSERT OR REPLACE INTO predictions 
           (user_id, match_url, my_pick, opponent, start_time) 
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, match_url, my_pick, opponent, start_time),
    )
    conn.commit()
    conn.close()


def add_to_history(user_id, match_name, predicted, winner, is_correct):
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


def is_match_posted(guild_id, match_url):
    """そのサーバーでその試合がすでに投稿済みかチェック"""
    conn = sqlite3.connect("data/predictions.db")
    c = conn.cursor()
    c.execute(
        "SELECT 1 FROM posted_matches WHERE guild_id = ? AND match_url = ?",
        (guild_id, match_url),
    )
    res = c.fetchone()
    conn.close()
    return res is not None


def mark_match_as_posted(guild_id, match_url):
    """そのサーバーに対して試合を投稿済みとして記録"""
    conn = sqlite3.connect("data/predictions.db")
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO posted_matches VALUES (?, ?)", (guild_id, match_url)
    )
    conn.commit()
    conn.close()


def set_guild_channel(guild_id, channel_id):
    """サーバーごとの投稿チャンネルを保存・更新"""
    conn = sqlite3.connect("data/predictions.db")
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO guild_settings VALUES (?, ?)", (guild_id, channel_id)
    )
    conn.commit()
    conn.close()


def get_all_guild_settings():
    """全サーバーの設定を取得"""
    conn = sqlite3.connect("data/predictions.db")
    c = conn.cursor()
    c.execute("SELECT guild_id, channel_id FROM guild_settings")
    rows = c.fetchall()
    conn.close()
    return rows
