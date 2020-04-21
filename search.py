import queue

from requests import get
import discord
from discord.ext import commands

class Booru(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.qe = ""
        self.msg_log = queue.LifoQueue() # need to do something about this
        self.shortcut = {
            'kc': 'kantai_collection',
            'al': 'azur_lane',
            'gf': 'girls_frontline',
            'ak': 'arknights',
            'fgo': 'fate/grand_order',
            'pk': 'pokemon'
            # any more?
        }


    @commands.command(description="calls the last search again")
    async def re(self, ct):
        data = await self.search(self.qe)
        if data:
            try:
                msg = data['file_url']
            except KeyError:
                msg = f"rip no perms to access image data\n<https://danbooru.donmai.us/posts/{data['id']}>"
            sent = await ct.send(msg)
            self.msg_log.put((sent, data))
        else:
            await ct.send("nothing found")


    @commands.command(description="search for an image on danbooru\nlimit to 2 tags because I am poor")
    async def br(self, ct, *args):
        self.qe = list(map(self.short, args))
        await self.re(ct)


    @commands.command(name='del', description="deletes the last image sent")
    async def delete(self, ct):
        try:
            msg = self.msg_log.get(0)[0]
            await msg.delete()
        except queue.Empty:
            pass

    
    @commands.command()
    async def info(self, ct):
        try:
            top = self.msg_log.get(0)
        except queue.Empty:
            return
        data = top[1]
        self.msg_log.put(top)
        
        embed = discord.Embed(title=f"https://danbooru.donmai.us/posts/{data['id']}", url=f"https://danbooru.donmai.us/posts/{data['id']}", description=data['created_at'])
        for cat in "character copyright artist general".split():
            embed.add_field(name=cat, value=data[f"tag_string_{cat}"].replace("_", "\\_"), inline=cat[0]=='c') # lmao that's so stupid but it works
        embed.set_footer(text="brought to you by CFZ")
        try:
            embed.set_thumbnail(url=data['preview_file_url'])
        except KeyError:
            pass

        await ct.send(embed=embed)


    @staticmethod
    async def search(tags):
        param = {
            'limit': 1,
            'tags': " ".join(tags[:2]),
            'random': 'true'
        }
        try:
            r = get(url="https://danbooru.donmai.us/posts.json", params=param, timeout=2)

        except err: # this shouldn't happen
            with open('log.txt', 'a') as f:
                f.write(f"request failed:   {str(err)}")
            return

        if not r.ok: # this shouldn't happen either
            with open('log.txt', 'a') as f:
                f.write(f"response not ok:   {str(r)}")
            return

        res = r.json()
        if res:
            return res[0]


    # for shortcut command- ie. yuudachi,kc -> yuudachi_(kantai_collection)
    def short(self, x):
        a = x.split(",")
        if len(a) == 2:
            try:
                a[1] = self.shortcut[a[1]]
            except KeyError:
                pass
            return f"{a[0]}_({a[1]})"
        return x


class Extra(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("ok.png", "rb") as k:
            self.ok_img = discord.File(k)


    @commands.command(description="ok")
    async def ok(self, ct):
        await ct.send(content="ok", file=self.ok_img)
