import requests


def get_vlr_matches():
    url = "https://vlrggapi.vercel.app/match?q=upcoming"
    try:
        response = requests.get(url)
        data = response.json()

        all_matches = data.get("data", {}).get("segments", [])
        tier1_matches = []

        for match in all_matches:
            event_name = match.get("match_event", "")
            team1 = match.get("team1", "")
            team2 = match.get("team2", "")

            # Tier 1判定
            is_tier1 = any(
                k in event_name for k in ["VCT", "Champions", "Masters", "Kickoff"]
            )
            is_tier2_or_gc = any(
                k in event_name for k in ["Challengers", "Game Changers"]
            )

            # 🛠️ TBDチェック：どちらかのチーム名に "TBD" が含まれていたらスキップ
            is_tbd = "TBD" in team1.upper() or "TBD" in team2.upper()

            # 全ての条件を満たす場合のみ追加
            if is_tier1 and not is_tier2_or_gc and not is_tbd:
                tier1_matches.append(match)

        return tier1_matches
    except Exception as e:
        print(f"Error fetching matches: {e}")
        return []


def get_vlr_results():
    url = "https://vlrggapi.vercel.app/match?q=results"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        return data.get("data", {}).get("segments", [])
    except Exception as e:
        print(f"API Fetch Error (Results): {e}")
        return []
