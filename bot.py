import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

import search

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='-')

play = discord.Activity(name="with loli", type=discord.ActivityType.playing)
watch = discord.Activity(name="loli", type=discord.ActivityType.watching)
listen = discord.Activity(name="loli", type=discord.ActivityType.listening)


@bot.event
async def on_ready():
    print("{} connected".format(bot.user))
    await bot.change_presence(activity=watch)


bot.add_cog(search.Booru(bot))

bot.run(TOKEN)