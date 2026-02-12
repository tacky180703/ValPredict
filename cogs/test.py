import discord
from discord.ext import commands
import sqlite3
from utils.db_manager import add_to_history
from components.match_cards import result_card_embed, match_card_embed, PredictionView


class TestCommandsDebug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="testmatch")
    async def test_match(self, ctx):
        mock_match = {
            "team1": "ZETA",
            "team2": "DFM",
            "match_event": "VCT Pacific",
            "match_page": "/test",
            "time_until_match": "1h",
        }

        embed = match_card_embed(mock_match)
        view = PredictionView(
            mock_match["team1"], mock_match["team2"], mock_match["match_page"]
        )
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
