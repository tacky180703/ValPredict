import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from utils.db_manager import set_guild_channel  # インポートが必要


class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="predict", description="現在の予想を表示します。")
    async def my_vote(self, interaction: discord.Interaction):
        await interaction.response.defer()
        conn = sqlite3.connect("data/predictions.db")
        c = conn.cursor()
        c.execute(
            "SELECT match_url, my_pick, opponent FROM predictions WHERE user_id = ?",
            (interaction.user.id,),
        )
        rows = c.fetchall()
        conn.close()

        res = "🤔 **あなたの現在の予想:**\n\n"
        if not rows:
            res += "現在、進行中の予想はありません。"
        else:
            for row in rows:
                url, my_pick, opponent = row
                match_title = f"{my_pick} vs {opponent}"
                res += f" **[{match_title}]({url})**\n予想: **{my_pick}**\n---\n"

        await interaction.followup.send(res)

    @app_commands.command(name="stats", description="自分の戦績を表示します")
    async def stats(self, interaction: discord.Interaction):
        await interaction.response.defer()
        conn = sqlite3.connect("data/predictions.db")
        c = conn.cursor()
        c.execute(
            "SELECT COUNT(*), SUM(is_correct) FROM history WHERE user_id = ?",
            (interaction.user.id,),
        )
        total, corrects = c.fetchone()
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
            history_text += f"{result_emoji} {h[0]}\n  予想: {h[1]}\n"

        embed = discord.Embed(
            title=f"📊 **{interaction.user.display_name}さんの戦績**",
            color=discord.Color.blue(),
        )
        embed.add_field(name="的中/合計:", value=f"{corrects} / {total}", inline=True)
        embed.add_field(name="的中率:", value=f"{rate:.1f}%", inline=True)
        embed.add_field(
            name="履歴（直近5試合）", value=history_text or "履歴なし", inline=False
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="setchannel",
        description="【管理者用】試合予想を自動投稿するチャンネルを設定します",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        try:
            set_guild_channel(interaction.guild_id, channel.id)
            await interaction.response.send_message(
                f"✅ 設定完了！今後、新着試合は {channel.mention} に自動投稿されます。",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ エラーが発生しました: {e}", ephemeral=True
            )

    @set_channel.error
    async def set_channel_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "⚠️ このコマンドはサーバー管理者のみ実行可能です。", ephemeral=True
            )

    @app_commands.command(name="cleardata", description="データを削除します。")
    async def clear_my_data(self, interaction: discord.Interaction):
        await interaction.response.defer()
        conn = sqlite3.connect("data/predictions.db")
        c = conn.cursor()
        c.execute("DELETE FROM predictions WHERE user_id = ?", (interaction.user.id,))
        c.execute("DELETE FROM history WHERE user_id = ?", (interaction.user.id,))
        conn.commit()
        conn.close()
        await interaction.followup.send(
            f"🗑️ {interaction.user.mention}さんのすべてのデータを削除しました。"
        )


async def setup(bot):
    await bot.add_cog(UserCog(bot))
