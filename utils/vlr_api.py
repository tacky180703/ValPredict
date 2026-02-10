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

            # --- Tier 1 判定ロジック ---
            # 大会名に VCT, Champions, Masters, Kickoff のいずれかが含まれるか
            # かつ、Challengers(Tier2) や Game Changers を除外する
            is_tier1 = any(
                k in event_name for k in ["VCT", "Champions", "Masters", "Kickoff"]
            )
            is_tier2_or_gc = any(
                k in event_name for k in ["Challengers", "Game Changers"]
            )

            if is_tier1 and not is_tier2_or_gc:
                tier1_matches.append(match)

        return tier1_matches
    except Exception as e:
        print(f"APIエラー: {e}")
        return []
