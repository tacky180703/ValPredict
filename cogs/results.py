import discord
import datetime
from discord.ext import commands, tasks
import sqlite3
from utils.helpers import get_timestamp
from utils.db_manager import add_to_history, get_all_guild_settings
from utils.vlr_api import get_vlr_results
from utils.embeds import result_card_embed

every_hour = [datetime.time(hour=h, minute=0) for h in range(24)]


class ResultChecker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_results.start()

    def cog_unload(self):
        self.check_results.cancel()

    @tasks.loop(time=every_hour)
    async def check_results(self):
        await self.bot.wait_until_ready()

        print(f"[{get_timestamp()}] 🔄 VLR結果チェックを開始します...")

        # VLR APIから最新の結果を取得
        results = get_vlr_results()
        if not results:
            print(f"[{get_timestamp()}] ⚠️ APIから結果を取得できませんでした。")
            return

        conn = sqlite3.connect("data/predictions.db")
        c = conn.cursor()

        # 現在DBに予想データが存在する試合のURLリストを取得
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

            # 取得した結果が、DBで管理している試合と一致するかチェック
            if any(match_path in url for url in active_match_urls):
                score1 = int(res.get("score1", 0))
                score2 = int(res.get("score2", 0))

                # 勝者の判定
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

                    result_embed = result_card_embed(
                        match=res, winner=winner, score1=score1, score2=score2
                    )
                    for guild_id, channel_id in guild_settings:
                        channel = self.bot.get_channel(channel_id)
                        if channel:
                            try:
                                await channel.send(embed=result_embed)
                            except Exception as e:
                                print(f"   ⚠️ ギルド {guild_id} への全体通知失敗: {e}")

                    # 2. 個別の的中確認と履歴保存
                    c.execute(
                        "SELECT user_id, my_pick FROM predictions WHERE match_url LIKE ?",
                        (f"%{match_path}%",),
                    )
                    voters = c.fetchall()

                    for user_id, my_pick in voters:
                        is_correct = 1 if my_pick == winner else 0

                        # ユーザーの戦績履歴に保存
                        add_to_history(
                            user_id,
                            f"{res['team1']} vs {res['team2']}",
                            my_pick,
                            winner,
                            is_correct,
                        )

                        # 個人へのDM通知
                        try:
                            user = await self.bot.fetch_user(user_id)
                            status_str = "✅ 的中" if is_correct else "❌ ハズレ"
                            await user.send(
                                f"【結果発表】{res['team1']} vs {res['team2']}\n"
                                f"勝者: **{winner}**\nあなたの予想: {my_pick} ({status_str}！)"
                            )
                            print(f"   ∟ 📩 DM送信完了: {user.name} ({status_str})")
                        except Exception as e:
                            print(f"   ∟ ⚠️ DM送信失敗 (ID: {user_id}): {e}")

                    # 3. 判定が終わった予想データをDBから削除
                    c.execute(
                        "DELETE FROM predictions WHERE match_url LIKE ?",
                        (f"%{match_path}%",),
                    )
                    conn.commit()

        conn.close()
        if processed_matches > 0:
            print(
                f"[{get_timestamp()}] ✅ 完了。{processed_matches}件の試合結果を処理しました。"
            )
        else:
            print(f"[{get_timestamp()}] ☕ 新しく確定した試合はありませんでした。")


async def setup(bot):
    await bot.add_cog(ResultChecker(bot))
