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
