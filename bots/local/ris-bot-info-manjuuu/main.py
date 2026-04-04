import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from services.randam_string_service import RandamStringService

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="/manjuuu_commands ", intents=intents)
randam_string_service = RandamStringService()


@bot.command()
async def health_check(ctx):
    """
    処理概要:
        1. ヘルスチェックメッセージを送信
    
    Args:
        ctx: Discordのコンテキストオブジェクト
    
    Returns:
        None
    """
    # 1. ヘルスチェックメッセージを送信
    await ctx.send("生きてますよ！")


@bot.command()
async def random_game_title(ctx):
    """
    処理概要:
        1. ランダムなゲームタイトルを送信
    
    Args:
        ctx: Discordのコンテキストオブジェクト
    
    Returns:
        None
    """
    # 1. ランダムなゲームタイトルを送信
    await randam_string_service.send_random_game_title(ctx.message)


bot.run(DISCORD_BOT_TOKEN)
