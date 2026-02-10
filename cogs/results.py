import discord
from discord.ext import commands, tasks
import sqlite3
import requests
from utils.helpers import get_timestamp
from utils.db_manager import add_to_history
from utils.vlr_api import get_vlr_results


class ResultChecker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_results.start()

    @tasks.loop(hours=1)
    async def check_results(self):
        await self.bot.wait_until_ready()

        print(f"[{get_timestamp()}] 🔄 VLR結果チェックを開始します...")

        results = get_vlr_results()

        conn = sqlite3.connect("data/predictions.db")
        c = conn.cursor()
        c.execute("SELECT DISTINCT match_url FROM predictions")
        # DB内のURLは /613928/... 形式かフルURLか確認が必要ですが、APIに合わせます
        active_match_urls = [row[0] for row in c.fetchall()]

        if not active_match_urls:
            print(f"[{get_timestamp()}] 💤 待機中の予想はありません。")
            conn.close()
            return

        processed_matches = 0
        for res in results:
            match_path = res.get("match_page")

            # APIの match_page は "/613928/..." なので、DB保存形式と照合
            # DBにフルURLで保存している場合は adjust が必要
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

                    # この試合の全予想者を取得
                    # DB内のURLに match_path が含まれるものを検索
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

                        try:
                            user = await self.bot.fetch_user(user_id)
                            status = "✅ 的中" if is_correct else "❌ ハズレ"
                            await user.send(
                                f"【結果発表】{res['team1']} vs {res['team2']}\n勝者: **{winner}**\nあなたの予想: {my_pick} ({status}！)"
                            )
                            print(f"   ∟ 📩 通知送信完了: {user.name} ({status})")
                        except Exception as e:
                            print(f"   ∟ ⚠️ 通知失敗 (ID: {user_id}): {e}")

                    # 判定が終わったデータを削除
                    c.execute(
                        "DELETE FROM predictions WHERE match_url LIKE ?",
                        (f"%{match_path}%",),
                    )
                    conn.commit()

        conn.close()
        if processed_matches > 0:
            print(
                f"[{get_timestamp()}] ✅ 処理完了: {processed_matches}件の試合を確定しました。"
            )
        else:
            print(f"[{get_timestamp()}] ☕ 新しい確定試合はありませんでした。")


async def setup(bot):
    await bot.add_cog(ResultChecker(bot))
