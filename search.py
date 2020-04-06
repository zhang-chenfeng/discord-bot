import requests


def danbooruSearch(tags):
    param = {
        'limit': 1,
        'tags': tags,
        'random': 'true'
    }

    r = requests.get(url="https://danbooru.donmai.us/posts.json", params=param, timeout=2)

    if not r.ok:
        print(str(r))
    
    res = r.json()
    if res:
        data = res[0]
        return data['file_url']


# more searches later
# but danbooru is all you need right

if __name__ == "__main__":
    tag = input("> ")
    print(danbooruSearch(tag))