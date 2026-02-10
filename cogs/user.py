import discord
from discord.ext import commands
from discord import app_commands
import sqlite3


class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="predict", description="現在の予想を表示します。")
    async def my_vote(self, interaction: discord.Interaction):
        await interaction.response.defer()

        conn = sqlite3.connect("data/predictions.db")
        c = conn.cursor()

        # 自分のIDに紐づくデータを取得
        c.execute(
            "SELECT match_url, my_pick, opponent FROM predictions WHERE user_id = ?",
            (interaction.user.id,),
        )
        rows = c.fetchall()

        res = "📊 **あなたの現在の予想:**\n\n"
        for row in rows:
            url, my_pick, opponent = row
            match_title = f"{my_pick} vs {opponent}"

            res += f"🏆 **[{match_title}]({url})**\n"
            res += f"予想: **{my_pick}**\n"
            res += "---" + "\n"

        await interaction.followup.send(res)

    @app_commands.command(name="stats", description="自分の戦績を表示します")
    async def stats(self, interaction: discord.Interaction):
        await interaction.response.defer()
        conn = sqlite3.connect("data/predictions.db")
        c = conn.cursor()

        # 1. 通算成績の取得
        c.execute(
            "SELECT COUNT(*), SUM(is_correct) FROM history WHERE user_id = ?",
            (interaction.user.id,),
        )
        total, corrects = c.fetchone()

        # 2. 直近5件の履歴を取得
        c.execute(
            "SELECT match_name, predicted_team, winner_team, is_correct FROM history WHERE user_id = ? ORDER BY date DESC LIMIT 5",
            (interaction.user.id,),
        )
        history_rows = c.fetchall()
        conn.close()

        if total == 0:
            await interaction.followup.send("まだ履歴がありません。")
            return

        corrects = corrects or 0
        rate = (corrects / total) * 100
        history_text = ""
        for h in history_rows:
            result_emoji = "✅" if h[3] == 1 else "❌"
            # h[0]:試合名, h[1]:予想, h[2]:勝者
            history_text += f"{result_emoji} {h[0]}\n  予想: {h[1]}\n"
        if not history_text:
            history_text = "履歴はありません。"

        embed = discord.Embed(
            title=f"📊 **{interaction.user.display_name}さんの戦績**\n",
            color=discord.Color.blue(),
        )
        embed.add_field(name="的中/合計:", value=f"{corrects} / {total}", inline=True)
        embed.add_field(name="的中率:", value=f"{rate:.1f}%", inline=True)
        embed.add_field(name="履歴（直近5試合）", value=history_text, inline=False)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="cleardata", description="データを削除します。")
    async def clear_my_data(self, interaction: discord.Interaction):
        await interaction.response.defer()
        conn = sqlite3.connect("data/predictions.db")
        c = conn.cursor()

        # 1. 現在進行中の予想を削除
        c.execute("DELETE FROM predictions WHERE user_id = ?", (interaction.user.id,))

        # 2. 過去の的中履歴を削除
        c.execute("DELETE FROM history WHERE user_id = ?", (interaction.user.id,))

        conn.commit()
        conn.close()

        await interaction.followup.send(
            f"🗑️ {interaction.user.mention}さんのすべてのデータを削除しました。"
        )


async def setup(bot):
    await bot.add_cog(UserCog(bot))
