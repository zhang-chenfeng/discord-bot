import os
import queue

from discord.ext import commands
from dotenv import load_dotenv

import search as websearch

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='-')

msg_log = {}

@bot.event
async def on_ready():
    print("{} connected".format(bot.user))


@bot.command(name='search')
async def search(ct, *args):
    response = websearch.danbooruSearch(args)
    if response:
        sent = await ct.send(response)
        try:
            msg_log[ct.author.id].put(sent)
        except KeyError:
            msg_log[ct.author.id] = queue.LifoQueue()
            msg_log[ct.author.id].put(sent)
    else: 
        await ct.send("nothing found")


@bot.command(name='del')
async def delete(ct):
    try:
        msg = msg_log[ct.author.id].get(0)
    except KeyError:
        pass
    except queue.Empty:
        pass
    else:
        await msg.delete()


@bot.command(name='exec')
async def ex(ct, cmd):
    exec(cmd)


bot.run(TOKEN)