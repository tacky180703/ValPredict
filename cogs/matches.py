import discord
import requests
from discord.ext import commands
from utils.helpers import get_region_color, get_team_logos, get_region


def get_vlr_matches():
    url = "https://vlrggapi.vercel.app/match?q=live_score"
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


class PredictionView(discord.ui.View):
    def __init__(self, team1, team2):
        super().__init__(timeout=None)  # タイムアウトなし
        self.team1 = team1
        self.team2 = team2

        self.predict_left.label = f"#{team1} WIN"
        self.predict_right.label = f"#{team2} WIN"

    @discord.ui.button(label="Loading...", style=discord.ButtonStyle.success)
    async def predict_left(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            f"✅ 「{self.team1}」の勝利を予想しました！", ephemeral=True
        )

    @discord.ui.button(label="Loading...", style=discord.ButtonStyle.danger)
    async def predict_right(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            f"✅ 「{self.team2}」の勝利を予想しました！", ephemeral=True
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

            view = PredictionView(match["team1"], match["team2"])

            await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Matches(bot))
