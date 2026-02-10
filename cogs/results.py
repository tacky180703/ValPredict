import discord
from discord.ext import commands, tasks
import sqlite3
from utils.helpers import get_timestamp
from utils.db_manager import add_to_history, get_all_guild_settings
from utils.vlr_api import get_vlr_results


class ResultChecker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_results.start()

    def cog_unload(self):
        self.check_results.cancel()

    @tasks.loop(hours=1)
    async def check_results(self):
        await self.bot.wait_until_ready()

        print(f"[{get_timestamp()}] 🔄 VLR結果チェックを開始します...")

        results = get_vlr_results()
        if not results:
            return

        conn = sqlite3.connect("data/predictions.db")
        c = conn.cursor()

        # 現在予想が存在する試合URLのリストを取得
        c.execute("SELECT DISTINCT match_url FROM predictions")
        active_match_urls = [row[0] for row in c.fetchall()]

        if not active_match_urls:
            print(f"[{get_timestamp()}] 💤 待機中の予想はありません。")
            conn.close()
            return

        processed_matches = 0
        guild_settings = get_all_guild_settings()

        for res in results:
            match_path = res.get("match_page")

            # 試合URLが一致するか確認
            if any(match_path in url for url in active_match_urls):
                score1 = int(res.get("score1", 0))
                score2 = int(res.get("score2", 0))

                winner = None
                if score1 > score2:
                    winner = res.get("team1")
                elif score2 > score1:
                    winner = res.get("team2")

                if winner:
                    processed_matches += 1
                    print(
                        f"[{get_timestamp()}] 🎯 試合終了検知: {res['team1']} {score1}-{score2} {res['team2']}"
                    )

                    # 1. サーバー全体への通知 (Embed)
                    result_embed = discord.Embed(
                        title="🏆 試合結果確定",
                        description=f"**{res['team1']}** vs **{res['team2']}**",
                        color=discord.Color.gold(),
                        url=f"https://www.vlr.gg{match_path}",
                    )
                    result_embed.add_field(
                        name="勝者", value=f"🥇 **{winner}**", inline=True
                    )
                    result_embed.add_field(
                        name="スコア", value=f"**{score1} - {score2}**", inline=True
                    )
                    result_embed.set_footer(text="的中した方はDMをご確認ください！")

                    for guild_id, channel_id in guild_settings:
                        channel = self.bot.get_channel(channel_id)
                        if channel:
                            try:
                                await channel.send(embed=result_embed)
                            except Exception as e:
                                print(f"   ⚠️ ギルド {guild_id} への全体通知失敗: {e}")

                    # 2. 個別の予想的中確認と履歴保存
                    c.execute(
                        "SELECT user_id, my_pick FROM predictions WHERE match_url LIKE ?",
                        (f"%{match_path}%",),
                    )
                    voters = c.fetchall()

                    for user_id, my_pick in voters:
                        is_correct = 1 if my_pick == winner else 0
                        add_to_history(
                            user_id,
                            f"{res['team1']} vs {res['team2']}",
                            my_pick,
                            winner,
                            is_correct,
                        )

                        # DM通知
                        try:
                            user = await self.bot.fetch_user(user_id)
                            status = "✅ 的中" if is_correct else "❌ ハズレ"
                            await user.send(
                                f"【結果発表】{res['team1']} vs {res['team2']}\n"
                                f"勝者: **{winner}**\nあなたの予想: {my_pick} ({status}！)"
                            )
                            print(f"   ∟ 📩 通知完了: {user.name} ({status})")
                        except Exception as e:
                            print(f"   ∟ ⚠️ 通知失敗 (ID: {user_id}): {e}")

                    # 3. 処理済みデータの削除
                    c.execute(
                        "DELETE FROM predictions WHERE match_url LIKE ?",
                        (f"%{match_path}%",),
                    )
                    conn.commit()

        conn.close()
        if processed_matches > 0:
            print(
                f"[{get_timestamp()}] ✅ 完了。{processed_matches}件の試合を確定しました。"
            )
        else:
            print(f"[{get_timestamp()}] ☕ 新しい確定試合はありませんでした。")


async def setup(bot):
    await bot.add_cog(ResultChecker(bot))
