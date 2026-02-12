import discord
import datetime
from discord.ext import commands, tasks
from utils.vlr_api import get_vlr_matches
from utils.helpers import get_timestamp
from utils.db_manager import (
    is_match_posted,
    mark_match_as_posted,
    get_all_guild_settings,
)
from components.match_cards import match_card_embed, PredictionView

every_hour = [datetime.time(hour=h, minute=0) for h in range(24)]


class MatchPoster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_post_matches.start()

    def cog_unload(self):
        self.auto_post_matches.cancel()

    @tasks.loop(time=every_hour)
    async def auto_post_matches(self):
        await self.bot.wait_until_ready()
        print(f"[{get_timestamp()}] 📡 Starting match update check...")

        guild_settings = get_all_guild_settings()
        if not guild_settings:
            return

        try:
            upcoming = get_vlr_matches()
        except Exception as e:
            print(f"[{get_timestamp()}] ❌ API Error (Poster): {e}")
            return

        new_matches_count = 0

        for guild_id, channel_id in guild_settings:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                continue

            for match in upcoming:
                match_url = match.get("match_page")

                if is_match_posted(guild_id, match_url):
                    continue

                embed = match_card_embed(match)

                view = PredictionView(match["team1"], match["team2"], match_url)

                try:
                    await channel.send(embed=embed, view=view)
                    mark_match_as_posted(guild_id, match_url)
                    new_matches_count += 1
                except Exception as e:
                    print(
                        f"[{get_timestamp()}] ⚠️ ギルド {guild_id} への投稿に失敗: {e}"
                    )

        if new_matches_count > 0:
            print(
                f"[{get_timestamp()}] ✅ Finished. Posted {new_matches_count} new matches."
            )
        else:
            print(f"[{get_timestamp()}] 💤 No new matches found.")

    @commands.command(name="post")
    @commands.has_permissions(administrator=True)
    async def manual_post(self, ctx):
        msg = await ctx.send("📡 Starting match update check... (Force Post Mode)")

        guild_settings = get_all_guild_settings()
        target_setting = next((s for s in guild_settings if s[0] == ctx.guild.id), None)

        if not target_setting:
            return await msg.edit(
                content="❌ このサーバーの投稿先チャンネルが設定されていません。"
            )

        channel_id = target_setting[1]
        channel = self.bot.get_channel(channel_id)

        try:
            upcoming = get_vlr_matches()
        except Exception as e:
            return await msg.edit(content=f"❌ API Error: {e}")

        if not upcoming:
            return await msg.edit(content="💤 No upcoming matches found on VLR.")

        posted_count = 0
        for match in upcoming:
            match_url = match.get("match_page")

            embed = match_card_embed(match)
            view = PredictionView(match["team1"], match["team2"], match_url)

            try:
                await channel.send(embed=embed, view=view)
                mark_match_as_posted(ctx.guild.id, match_url)
                posted_count += 1
            except Exception as e:
                print(f"[{get_timestamp()}] ⚠️ Manual post failure: {e}")

        await msg.edit(
            content=f"✅ Successfully posted {posted_count} matches to {channel.mention}!"
        )


async def setup(bot):
    await bot.add_cog(MatchPoster(bot))
