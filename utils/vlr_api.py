import requests


def get_vlr_matches():
    url = "https://vlrggapi.vercel.app/match?q=upcoming"
    try:
        response = requests.get(url)
        data = response.json()

        all_matches = data.get("data", {}).get("segments", [])

        return all_matches
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
