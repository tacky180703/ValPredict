import discord
from discord.ext import commands, tasks
from utils.vlr_api import get_vlr_matches
from utils.helpers import get_region, get_region_color, get_timestamp
from utils.db_manager import (
    is_match_posted,
    mark_match_as_posted,
    get_all_guild_settings,
    save_prediction,
)


class PredictionView(discord.ui.View):
    def __init__(self, team1, team2, match_url):
        super().__init__(timeout=None)
        self.team1 = team1
        self.team2 = team2
        self.match_url = match_url
        self.predict_left.label = f"{team1} WIN"
        self.predict_right.label = f"{team2} WIN"

    @discord.ui.button(style=discord.ButtonStyle.success)
    async def predict_left(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        try:
            save_prediction(interaction.user.id, self.match_url, self.team1, self.team2)
            await interaction.response.send_message(
                f"✅ 「{self.team1}」の勝利を予想しました！", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ エラー: {e}", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.danger)
    async def predict_right(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        try:
            save_prediction(interaction.user.id, self.match_url, self.team2, self.team1)
            await interaction.response.send_message(
                f"✅ 「{self.team2}」の勝利を予想しました！", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ エラー: {e}", ephemeral=True)


class MatchPoster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_post_matches.start()

    def cog_unload(self):
        self.auto_post_matches.cancel()

    @tasks.loop(minutes=1)
    async def auto_post_matches(self):
        await self.bot.wait_until_ready()
        print(f"[{get_timestamp()}] 📡 新着試合のチェックを開始...")

        guild_settings = get_all_guild_settings()
        if not guild_settings:
            return

        try:
            upcoming = get_vlr_matches()
        except Exception as e:
            print(f"[{get_timestamp()}] ❌ APIエラー (Poster): {e}")
            return

        new_matches_count = 0

        # 1. ギルドごとにループ
        for guild_id, channel_id in guild_settings:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                continue

            # 2. 試合ごとにループ
            for match in upcoming:
                match_url = match.get("match_page")

                # このサーバーで既に投稿済みならスキップ
                if is_match_posted(guild_id, match_url):
                    continue

                event_name = match.get("match_event", "Unknown Event")
                region_label = get_region(event_name)
                color = get_region_color(region_label)

                embed = discord.Embed(
                    title=f"📢 投票開始: {match['team1']} vs {match['team2']}",
                    url=(
                        f"https://www.vlr.gg{match_url}"
                        if not match_url.startswith("http")
                        else match_url
                    ),
                    color=color,
                )
                embed.add_field(name="大会名", value=event_name, inline=False)
                embed.add_field(
                    name="開始まで",
                    value=match.get("time_until_match", "不明"),
                    inline=True,
                )

                view = PredictionView(match["team1"], match["team2"], match_url)

                try:
                    await channel.send(embed=embed, view=view)
                    mark_match_as_posted(guild_id, match_url)
                    new_matches_count += 1
                except Exception as e:
                    print(
                        f"[{get_timestamp()}] ⚠️ ギルド {guild_id} への投稿に失敗: {e}"
                    )

        if new_matches_count > 0:
            print(
                f"[{get_timestamp()}] ✅ 完了。{new_matches_count}件の新着投稿がありました。"
            )
        else:
            print(f"[{get_timestamp()}] 💤 新しい試合はありません。")


async def setup(bot):
    await bot.add_cog(MatchPoster(bot))
