import discord
from discord.ext import commands, tasks
import sqlite3
from utils.vlr_api import get_vlr_matches
from utils.helpers import get_region, get_region_color, get_timestamp
from utils.db_manager import (
    is_match_posted,
    mark_match_as_posted,
    get_all_guild_settings,
)
from cogs.matches import PredictionView


class MatchPoster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_post_matches.start()

    def cog_unload(self):
        self.auto_post_matches.cancel()

    @tasks.loop(hours=1)
    async def auto_post_matches(self):
        await self.bot.wait_until_ready()

        print(f"[{get_timestamp()}] 📡 新着試合の自動チェックを開始...")

        # 設定済みの全サーバーのチャンネル設定を取得
        guild_settings = get_all_guild_settings()
        if not guild_settings:
            print(
                f"[{get_timestamp()}] 💤 投稿先が設定されているサーバーがないため、スキップします。"
            )
            return

        try:
            upcoming = get_vlr_matches()
        except Exception as e:
            print(f"[{get_timestamp()}] ❌ APIエラー (Poster): {e}")
            return

        new_matches_count = 0
        # 直近5試合のうち、未投稿のものがあれば各サーバーに投稿
        for match in upcoming[:5]:
            match_url = match.get("match_page")

            if is_match_posted(match_url):
                continue

            new_matches_count += 1
            event_name = match.get("match_event", "Unknown Event")
            region_label = get_region(event_name)
            color = get_region_color(region_label)

            # 投稿用Embedの作成
            embed = discord.Embed(
                title=f"📢 新規投票開始: {match['team1']} vs {match['team2']}",
                url=match_url,
                color=color,
            )
            embed.add_field(name="大会名", value=event_name, inline=False)
            embed.add_field(name="リージョン", value=region_label, inline=True)
            embed.add_field(
                name="開始まで", value=match["time_until_match"], inline=True
            )

            print(
                f"[{get_timestamp()}] 🆕 新着試合を検知: {match['team1']} vs {match['team2']}"
            )

            # 設定されているすべてのチャンネルに送信
            for guild_id, channel_id in guild_settings:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    view = PredictionView(match["team1"], match["team2"], match_url)
                    try:
                        await channel.send(embed=embed, view=view)
                        # print(f"   ∟ 📤 サーバー {guild_id} に投稿しました。")
                    except Exception as e:
                        print(f"   ∟ ⚠️ サーバー {guild_id} への投稿に失敗しました: {e}")

            # 最後に「投稿済み」としてマーク
            mark_match_as_posted(match_url)

        print(f"[{get_timestamp()}] ✅ チェック完了。新規投稿: {new_matches_count}件")


async def setup(bot):
    await bot.add_cog(MatchPoster(bot))
