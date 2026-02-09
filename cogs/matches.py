import discord
import requests
from discord.ext import commands
from utils.helpers import get_region_color, get_team_logos, get_region
from utils.db_manager import save_prediction
from utils.vlr_api import get_vlr_matches


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
            print(f"ERROR (Left Button): {e}")
            await interaction.response.send_message(
                f"❌ エラーが発生しました: {e}", ephemeral=True
            )

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
            print(f"ERROR (Right Button): {e}")
            await interaction.response.send_message(
                f"❌ エラーが発生しました: {e}", ephemeral=True
            )


class Matches(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def matches(self, ctx):
        # ここに matches コマンドの中身をコピペ
        # ※ self.bot を使う点に注意
        await ctx.send("Tier 1の試合スケジュールを確認中...")

        upcoming = get_vlr_matches()

        if not upcoming:
            await ctx.send("現在、予定されているTier 1の試合はありません。")
            return

        # 最初の5試合を表示
        for match in upcoming[:5]:
            event_name = match.get("match_event", "Unknown Event")
            region_label = get_region(event_name)
            color = get_region_color(region_label)

            embed = discord.Embed(
                title=f"{match['team1']} vs {match['team2']}", color=color
            )
            embed.add_field(name="大会名", value=event_name, inline=False)
            embed.add_field(name="リージョン", value=region_label, inline=True)
            embed.add_field(
                name="開始まで", value=match["time_until_match"], inline=True
            )

            embed.url = match.get("match_page")

            view = PredictionView(
                match["team1"], match["team2"], match.get("match_page")
            )

            await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Matches(bot))
