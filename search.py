from requests import get
import discord
from discord.ext import commands



class Node():
    def __init__(self, val, dat):
        self.val, self.dat = val, dat
        self.next = self.prev = None



class Log():
    def __init__(self, maxsize):
        self.head = self.tail = None
        self.maxsize = maxsize * (maxsize > 2) or 2
        self.size = 0
    
    
    def put(self, val, dat):
        n = Node(val, dat)
        try:
            self.head.prev = n
        except AttributeError:
            self.tail = n
        n.next = self.head
        self.head = n
        self.size += 1
        
        if self.size > self.maxsize:
            self.tail = self.tail.prev
            self.tail.next = None


    def top(self):
        return self.head
        
        
    def get(self):
        try:
            n = self.head
            self.head = n.next
        except AttributeError:
            raise
        else:
            try:
                self.head.prev = None
            except AttributeError:
                self.tail = None
            self.size -= 1
            return n
    
    
    def pr(self):
        a = self.head
        while a is not None:
            print(a.val, end=", ")
            a = a.next
        print()



class Booru(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.qe = ""
        self.msg_log = Log(200)
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
            self.msg_log.put(sent, data)
        else:
            await ct.send("nothing found")


    @commands.command(
        description="search for an image on danbooru\nlimit to 2 tags because I am poor", 
        help="""search in the same way as you do in danbooru
        can use all tags/metatags and other stuffs

        be careful as this can generate stuff that is against Discord TOS
        use the -del command if that happens
        - don't search sketchy stuff; don't -br lucky_star rating:e. just don't
        - plz just use the rating:s tag if you are searching stuff like shinobu

        SHORTCUTS
        1. use ',' to subsitute the '_(...)' part of a tag
            ie. manjuu_(azur_lane) -> manjuu,azur_lane

        2. specific common titles have an abbreviation- 
            ie. five-seven_(girls_frontline) -> five-seven_(gf)

            kc -> kantai_collection
            al -> azur_lane
            gf -> girls_frontline
            ak -> arknights
            fgo -> fate/grand_order

        3. both the above can be combined
            ie. yuudachi_(kantai_collection) -> yuudachi,kc"""
        )
    async def br(self, ct, *args):
        self.qe = list(map(self.short, args))
        await self.re(ct)
        

    @commands.command(
        name='del',
        description="deletes the last image sent",  
        help="""deletes the last image sent by the bot
        my implementation currently is really shitty and a massive memory leak
        
        use this if you make the bot pull up some loli hentai or something
        for that purpose anyone is able to use the command
        use it as intended and don't use it to grief other people's fap sessions"""
        )
    async def delete(self, ct):
        try:
            msg = self.msg_log.get().val
            await msg.delete()
        except AttributeError:
            pass

    
    @commands.command()
    async def info(self, ct):
        top = self.msg_log.top()
        if top is None:
            return
        data = top.dat
        embed = discord.Embed(title=f"https://danbooru.donmai.us/posts/{data['id']}", url=f"https://danbooru.donmai.us/posts/{data['id']}", description=data['created_at'], color=0xcfcfcf)
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
            c = {}
            for x in "id created_at file_url preview_file_url tag_string_character tag_string_copyright tag_string_artist tag_string_general".split():
                try:
                    c[x] = res[0][x]
                except KeyError:
                    pass
            return c


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



if __name__ == "__main__":
    a = input(">> ")
    while a != "exit":
        exec(a)
        a = input(">> ")