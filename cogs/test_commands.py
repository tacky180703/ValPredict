import discord
from discord.ext import commands
import sqlite3
from utils.helpers import get_region_color
from utils.db_manager import save_prediction, add_to_history

# テストでも同じViewを使いたいので、cogs.matchesからインポートするか
# もしくは utils.views に移動させているならそこからインポートします
from cogs.matches import PredictionView


class TestCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="testmatch")
    async def test_match(self, ctx):
        """テスト用の試合カードを表示"""
        mock_match = {
            "team1": "ZETA Division",
            "team2": "DetonatioN FocusMe",
            "match_event": "VCT Mock Tournament",
            "match_page": "https://www.vlr.gg/test-match-123",
            "time_until_match": "1h 30m",
        }
        color = get_region_color("Pacific")
        embed = discord.Embed(
            title=f"【TEST】{mock_match['team1']} vs {mock_match['team2']}",
            color=color,
            url=mock_match["match_page"],
        )
        embed.add_field(name="大会名", value=mock_match["match_event"], inline=False)

        view = PredictionView(
            mock_match["team1"], mock_match["team2"], mock_match["match_page"]
        )
        await ctx.send("🔧 テストモード:", embed=embed, view=view)

    @commands.command(name="testwin")
    async def test_win(
        self, ctx, *, winner: str
    ):  # "*" を付けるとスペース入りのチーム名も受け取れます
        """テスト試合の結果を確定させる"""
        test_url = "https://www.vlr.gg/test-match-123"
        conn = sqlite3.connect("data/predictions.db")
        c = conn.cursor()
        c.execute(
            "SELECT user_id, team_name FROM predictions WHERE match_url = ?",
            (test_url,),
        )
        predictions = c.fetchall()

        if not predictions:
            await ctx.send("この試合に予想している人はいません。")
            return

        for user_id, predicted_team in predictions:
            is_correct = 1 if predicted_team == winner else 0
            add_to_history(
                user_id, "TEST: ZETA vs DFM", predicted_team, winner, is_correct
            )

            user = await self.bot.fetch_user(user_id)
            msg = (
                f"🎊 {user.mention}さん、的中！"
                if is_correct
                else f"💀 {user.mention}さん、残念..."
            )
            await ctx.send(f"{msg} {winner}の勝利です！")

        c.execute("DELETE FROM predictions WHERE match_url = ?", (test_url,))
        conn.commit()
        conn.close()
        await ctx.send("✅ テスト判定完了。")


async def setup(bot):
    await bot.add_cog(TestCommands(bot))
