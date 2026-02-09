import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# --- VLR.ggをスクレイピングする関数 ---
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


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")


@bot.command()
async def matches(ctx):
    await ctx.send("Tier 1の試合スケジュールを確認中...")
    upcoming = get_vlr_matches()

    if not upcoming:
        await ctx.send("現在、予定されているTier 1の試合はありません。")
        return

    # 最初の5試合を表示
    for match in upcoming[:5]:
        event_name = match.get("match_event", "Unknown Event")

        # リージョン判定 (大会名から推測)
        if "Pacific" in event_name:
            color = discord.Color.blue()
            region_label = "Pacific"
        elif "Americas" in event_name:
            color = discord.Color.green()
            region_label = "Americas"
        elif "EMEA" in event_name:
            color = discord.Color.gold()
            region_label = "EMEA"
        elif "China" in event_name:
            color = discord.Color.red()
            region_label = "China"
        else:
            color = discord.Color.purple()
            region_label = "International"

        embed = discord.Embed(
            title=f"{match['team1']} vs {match['team2']}", color=color
        )
        embed.add_field(name="大会名", value=event_name, inline=False)
        embed.add_field(name="リージョン", value=region_label, inline=True)
        embed.add_field(name="開始まで", value=match["time_until_match"], inline=True)

        # 試合ページへのリンクも貼っておくと便利です
        embed.url = match.get("match_page")

        await ctx.send(embed=embed)


bot.run(TOKEN)
