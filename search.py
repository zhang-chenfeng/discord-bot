import os

import requests
from dotenv import load_dotenv


def danbooruSearch(tags):
    param = {
        'limit': 1,
        'tags': " ".join(tags[:2]),
        'random': 'true'
    }

    r = requests.get(url="https://danbooru.donmai.us/posts.json", params=param, timeout=2)

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

# more searches later
# but danbooru is all you need right

if __name__ == "__main__":
    tag = input("> ").split()
    print(danbooruSearch(tag))
    # load_dotenv()
    # TOKEN = os.getenv('DANBOORU_KEY')
