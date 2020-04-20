import queue

from requests import get
from discord.ext import commands

class Booru(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.qe = ""
        self.msg_log = queue.LifoQueue()
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
        response = await self.search(self.qe)
        if response:
            sent = await ct.send(response)
            self.msg_log.put(sent)
        else:
            await ct.send("nothing found")


    @commands.command(description="search for an image on danbooru\nlimit to 2 tags because I am poor")
    async def br(self, ct, *args):
        self.qe = list(map(self.short, args))
        await self.re(ct)


    @commands.command(name='del', description="deletes the last image sent")
    async def delete(self, ct):
        try:
            msg = self.msg_log.get(0)
            await msg.delete()
        except queue.Empty:
            pass


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
            data = res[0]
            try:
                return f"<https://danbooru.donmai.us/posts/{data['id']}>\n{data['file_url']}"
            except KeyError:
                return f"rip no perms to access image data\n<https://danbooru.donmai.us/posts/{data['id']}>"


    # for shortcut command- ie. yuudachi,kc -> yuudachi_(kantai_collection)
    @staticmethod
    def short(x):
        a = x.split(",")
        if len(a) == 2:
            try:
                a[1] = self.shortcut[a[1]]
            except KeyError:
                pass
            return f"{a[0]}_({a[1]})"
        return x
    
        
