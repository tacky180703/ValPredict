import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from utils.db_manager import init_db
from components.match_cards import PredictionView

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    bot.add_view(PredictionView())
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Sync Error: {e}")

    print(f"Logged in as {bot.user.name}")


async def load_extensions():
    if not os.path.exists("./cogs"):
        os.makedirs("./cogs")

    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"成功: {filename} を読み込みました")
            except Exception as e:
                print(f"失敗: {filename} の読み込み中にエラーが発生しました: {e}")


async def main():
    async with bot:
        init_db()
        await load_extensions()
        await bot.start(TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
