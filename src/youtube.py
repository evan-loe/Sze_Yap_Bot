import requests
from dotenv import load_dotenv
from os import getenv, path
import sys
import time
from datetime import datetime, timedelta
from urllib.parse import quote
from discord import Webhook
from discord.webhook import RequestsWebhookAdapter
import re
from cogs.jsonfxn import save_json, open_datajson

load_dotenv()
YOUTUBE_TOKEN = getenv("YOUTUBE_TOKEN")

BASE_URL = "https://www.youtube.com/watch?v="

headers = {
    'Accept': 'application/json'
}

toolbar_width = 60

__location__ = path.dirname(__file__)

while True:
    start_time = datetime.now()
    print(start_time)
    sys.stdout.write("[%s]" % (" " * toolbar_width))
    sys.stdout.flush()
    sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

    for i in range(toolbar_width):
        time.sleep(60)
        sys.stdout.write("-")
        sys.stdout.flush()

    sys.stdout.write("]\n") # this ends the progress bar
    
    params = {
        'part': 'snippet',
        'maxResults': '25',
        'q': 'taishanese%&C台山話',
        'key': YOUTUBE_TOKEN,
        'publishedAfter': start_time.replace(microsecond=0).isoformat() + "Z",
        'publishedBefore': (start_time + timedelta(hours=1)).replace(microsecond=0).isoformat() + "Z",
    }
    print(params)
    
    response = requests.get('https://youtube.googleapis.com/youtube/v3/search', headers=headers, params=params)
    search_json = response.json()
    print(search_json)
    
    data = open_datajson('system')
    for link in data['system']['youtube']:
        match = re.search(r"discord(app)?\.com\/api\/webhooks\/(?P<id>\d+)\/(?P<token>.+)", link)
        webhook = Webhook.partial(
            match.group("id"), match.group("token"),
            adapter=RequestsWebhookAdapter())
    
        for item in search_json.setdefault('items', []):
            webhook.send(BASE_URL+item['id']['videoId'])
    
    if len(search_json['items']) > 0:
        data['system']['youtube_count'] += 1
        save_json(path.join(__location__, 'cogs', 'data.json'), data)