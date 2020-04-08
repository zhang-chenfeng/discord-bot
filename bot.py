import os
import queue

import discord
from discord.ext import commands
from dotenv import load_dotenv
from requests import get

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='-')

play = discord.Activity(name="with loli", type=discord.ActivityType.playing)
watch = discord.Activity(name="loli", type=discord.ActivityType.watching)
listen = discord.Activity(name="loli", type=discord.ActivityType.listening)


msg_log = queue.LifoQueue()
shortcut = {
    'kc': 'kantai_collection',
    'al': 'azur_lane',
    'gf': 'girls_frontline',
    'ak': 'arknights',
    'pk': 'pokemon',
    'fgo': 'fate/grand_order'
    }
bot.qe = ""

@bot.event
async def on_ready():
    print("{} connected".format(bot.user))
    await bot.change_presence(activity=play)


@bot.command(name='search', description="search for an image on danbooru\nlimit to 2 tags because I am poor")
async def search(ct, *args):
    bot.qe = list(map(short, args))
    await rerun(ct)


@bot.command(name='del', description="deletes the last image sent")
async def delete(ct):
    try:
        msg = msg_log.get(0)
        await msg.delete()
    except queue.Empty:
        pass


@bot.command(name='re', description="calls the last search again")
async def rerun(ct): # lmao nice copy paste
    response = await danbooruSearch(bot.qe)
    if response:
        sent = await ct.send(response)
        msg_log.put(sent)
    else:
        await ct.send("nothing found")


@bot.command(name='exec')
async def ex(ct, cmd):
    exec(cmd)


async def danbooruSearch(tags):
    param = {
        'limit': 1,
        'tags': " ".join(tags[:2]),
        'random': 'true'
    }

    r = get(url="https://danbooru.donmai.us/posts.json", params=param, timeout=2)

    if not r.ok:
        print(str(r))
        return
    
    res = r.json()
    if res:
        data = res[0]
        try:
            return f"<https://danbooru.donmai.us/posts/{data['id']}>\n{data['file_url']}"
        except KeyError:
            return f"rip no perms to access image data\n<https://danbooru.donmai.us/posts/{data['id']}>"


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