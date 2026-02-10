import discord
from discord.ext import commands
import sqlite3
from utils.helpers import get_region_color
from utils.db_manager import add_to_history
from utils.embeds import result_card_embed, match_card_embed
from cogs.poster import PredictionView


class TestCommandsDebug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="testm")
    async def test_match(self, ctx):
        test_path = "/test-match-123"
        team1, team2 = "ZETA", "DFM"
        event = "VCT Pacific Mock Tournament"
        time_str = "1h 30m"

        embed = match_card_embed(
            team1=team1, team2=team2, url=test_path, time=time_str, event_name=event
        )
        view = PredictionView(team1, team2, test_path)
        await ctx.send(
            embed=embed,
            view=view,
        )

    @commands.command(name="testr")
    async def test_win(self, ctx, winner: str, score1: int = 2, score2: int = 1):
        test_url = "/test-match-123"

        result_embed = result_card_embed(
            "ZETA",
            "DFM",
            winner,
            score1,
            score2,
            test_url,
            "VCT Pacific Mock Tournament",
        )
        await ctx.send(embed=result_embed)

        # 2. DBから予想者を取得して個別通知
        conn = sqlite3.connect("data/predictions.db")
        c = conn.cursor()
        c.execute(
            "SELECT user_id, my_pick FROM predictions WHERE match_url = ?", (test_url,)
        )
        predictions = c.fetchall()

        if not predictions:
            await ctx.send("❌ 予想データが見つかりませんでした。")
            conn.close()
            return

        for user_id, my_pick in predictions:
            is_correct = 1 if my_pick == winner else 0
            add_to_history(user_id, "TEST: ZETA vs DFM", my_pick, winner, is_correct)

            user = await self.bot.fetch_user(user_id)
            status = "✅ 的中" if is_correct else "❌ ハズレ"
            # DM 形式のテスト
            try:
                await user.send(
                    f"【テスト結果発表】勝者: **{winner}** / 予想: {my_pick} ({status})"
                )
            except:
                await ctx.send(f"⚠️ {user.mention} へのDM送信に失敗しました。")

        c.execute("DELETE FROM predictions WHERE match_url = ?", (test_url,))
        conn.commit()
        conn.close()


async def setup(bot):
    await bot.add_cog(TestCommandsDebug(bot))
