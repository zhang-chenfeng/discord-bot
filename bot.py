import os
import queue

from discord.ext import commands
from dotenv import load_dotenv

import search as websearch

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='-')

msg_log = queue.LifoQueue()
shortcut = {
    'kc': 'kantai_collection',
    'al': 'azur_lane',
    'gf': 'girls_frontline',
    'ak': 'arknights',
    'pk': 'pokemon'
    'fgo': 'fate/grand_order'
    }

@bot.event
async def on_ready():
    print("{} connected".format(bot.user))


@bot.command(name='search', description="search for an image on danbooru\nlimit to 2 tags because I am poor")
async def search(ct, *args):
    cleaned = list(map(short, args))
    response = websearch.danbooruSearch(cleaned)
    if response:
        sent = await ct.send(response)
        msg_log.put(sent)
    else:
        await ct.send("nothing found")


@bot.command(name='del', description="deletes the last image sent")
async def delete(ct):
    try:
        msg = msg_log.get(0)
        await msg.delete()
    except queue.Empty:
        pass


@bot.command(name='exec')
async def ex(ct, cmd):
    exec(cmd)


def short(x):
    a = x.split(",")
    if len(a) == 2:
        try:
            a[1] = shortcut[a[1]]
        except KeyError:
            pass
        return f"{a[0]}_({a[1]})"
    return x


bot.run(TOKEN)