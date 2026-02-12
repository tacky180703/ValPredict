import discord
import requests
import datetime
from bs4 import BeautifulSoup


def get_unix_timestamp(time_str):
    if not time_str:
        return 0
    try:
        dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        dt = dt.replace(tzinfo=datetime.timezone.utc)
        return int(dt.timestamp())
    except Exception as e:
        print(f"Timestamp Error: {e}")
        return 0


def format_vlr_url(path):
    if not path:
        return ""
    return f"https://www.vlr.gg{path}" if not path.startswith("http") else path


def get_region_color(region_name):
    colors = {
        "Pacific": "#49C2CC",
        "EMEA": "#D4FF1D",
        "Americas": "#F15922",
        "China": "#FC2659",
        "INTL": "#6F4ACC",
    }

    hex_code = colors.get(region_name, "#808080")

    return discord.Color.from_str(hex_code)


def get_region(event_name):
    event_name = event_name.lower()
    if "pacific" in event_name:
        return "Pacific"
    elif "americas" in event_name:
        return "Americas"
    elif "emea" in event_name:
        return "EMEA"
    elif "china" in event_name:
        return "China"
    elif "challengers" in event_name or "split" in event_name:
        return "Challengers"
    elif "game changers" in event_name:
        return "Game Changers"

    return "Other"


def get_team_logos(match_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(match_url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        t1_logo_el = soup.select_one(".match-header-link.mod-1 img")
        t2_logo_el = soup.select_one(".match-header-link.mod-2 img")

        logos = []
        for el in [t1_logo_el, t2_logo_el]:
            if el:
                src = el.get("src")
                full_url = f"https:{src}" if src.startswith("//") else src
                logos.append(full_url)
            else:
                logos.append(None)

        return logos
    except Exception as e:
        print(f"ロゴ取得エラー: {e}")
        return [None, None]


def get_timestamp():
    import datetime

    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
