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


# --- VLR.ggから直接データを引っこ抜く関数 ---
def scrape_vlr_events():
    url = "https://www.vlr.gg/events"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        event_list = []
        items = soup.select(".event-item")

        for item in items[:5]:
            # 大会名
            title = item.select_one(".event-item-title").get_text().strip()
            # ステータス（Ongoing/Upcoming）
            status = item.select_one(".event-item-desc-item-status").get_text().strip()

            tier_label = item.select_one('.event-item-desc-item:contains("Tier")')

            is_tier1 = False
            if tier_label and "Tier 1" in tier_label.get_text():
                is_tier1 = True
            elif any(
                keyword in title
                for keyword in ["Champions", "Masters", "Kickoff", "VCT"]
            ):
                is_tier1 = True

            if is_tier1:
                event_list.append({"title": title, "status": status})

        return event_list
    except Exception as e:
        print(f"スクレイピングエラー: {e}")
        return []


@bot.event
async def on_ready():
    print(f"ログイン成功: {bot.user.name}")


@bot.command()
async def list_events(ctx):
    await ctx.send("VLR.ggから最新の大会情報を直接取得中...")
    vlr_events = scrape_vlr_events()

    if not vlr_events:
        await ctx.send(
            "データを取得できませんでした。サイトの構造が変わった可能性があります。"
        )
        return

    embed = discord.Embed(title="現在・近日開催の大会", color=discord.Color.green())
    for ev in vlr_events:
        embed.add_field(
            name=ev["title"], value=f"ステータス: {ev['status']}", inline=False
        )

    await ctx.send(embed=embed)


bot.run(TOKEN)
