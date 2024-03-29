import discord
from discord.webhook import RequestsWebhookAdapter
from dotenv import load_dotenv
import os
import requests
import json
from discord import Embed
from dateutil.parser import isoparse
from discord import Webhook
import re
import time
import traceback
from datetime import datetime
from cogs.jsonfxn import open_datajson, save_json

load_dotenv()
BEARER_TOKEN = os.getenv('TWITTER_TOKEN')

__location__ = os.path.dirname(__file__)

class TooManyConnections(Exception):
    pass

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def get_rules(headers):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", headers=headers
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    return response.json()

def delete_all_rules(headers, rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    print(ids)
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload
    )
    print("Deleted Rules")
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    # print(json.dumps(response.json()))


def set_rules(headers, rules):
    
    payload = {"add": rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload
    )
    print("Setting Rules")
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    # print(json.dumps(response.json()))


def get_stream(headers):
    counter = 1
    payload = {
        'tweet.fields': 'created_at,public_metrics,author_id,lang',
        'expansions': 'author_id,attachments.media_keys',
        'user.fields': 'profile_image_url',
        'media.fields': 'preview_image_url,url'
    }
    with requests.get("https://api.twitter.com/2/tweets/search/stream", headers=headers, stream=True, params=payload) as response:
        if response.status_code != 200:
            if response.status_code == 429 and response.json().setdefault('connection_issue', 'error') == "TooManyConnections":
                raise TooManyConnections()
            raise Exception(
                "Cannot get stream (HTTP {}): {}".format(
                    response.status_code, response.text
                )
            )
        for response_line in response.iter_lines():
            if response_line:
                
                tweet = json.loads(response_line)
                # print(json.dumps(tweet, indent=4, sort_keys=True))
                print(tweet)
                link = f"https://twitter.com/{tweet['data']['author_id']}"\
                    f"/statuses/{tweet['data']['id']}"
                print(f"{tweet['data']['text']}\nMatched Rule: {[rule['tag'] for rule in tweet['matching_rules']]}\n")
                embed = Embed(
                    description=f"{tweet['data']['text']}\n\n[Tweet]({link})",
                    timestamp=isoparse(tweet['data']['created_at']),
                    colour=discord.Color.from_rgb(29, 161, 242))
                user = tweet['includes']['users'][0]
                embed.set_author(
                    name=f"{user['name']} "
                    f"(@{user['username']})",
                    icon_url=user['profile_image_url'],
                    url=f"https://www.twitter.com/{user['username']}")
                if 'media' in tweet['includes'].keys():
                    if 'url' in tweet['includes']['media'][0]:
                        embed.set_image(url=tweet['includes']['media'][0]['url'])
                    elif 'preview_image_url' in tweet['includes']['media'][0]:
                        embed.set_image(url=tweet['includes']['media'][0]['preview_image_url'])
                
                embed.set_footer(text=f'Twitter', icon_url="https://help.twitter.com/content/dam/help-twitter/brand/logo.png")
                
                data = open_datajson('system')
                
                for link in data['system']['twitter']:
                    match = re.search(r"discord(app)?\.com\/api\/webhooks\/(?P<id>\d+)\/(?P<token>.+)", link)
                    webhook = Webhook.partial(
                        match.group("id"), match.group("token"),
                        adapter=RequestsWebhookAdapter())
                    
                    webhook.send(embed=embed)
                data['system']['tweet_count'] += 1
                save_json(os.path.join(__location__, 'cogs', 'data.json'), data)

def start_webhook():
    rules = [
        {"value": '(新會 OR 開平 OR 恩平 OR 恩平話 OR 新會話 OR 開平話 OR 台山 OR 台山話 OR 四邑 OR 四邑方言 OR 台山醬) -is:retweet (lang:en OR lang:zh-TW OR lang:zh OR lang:und) -is:reply',
         "tag": 'chinese chars'},
        {"value": '("Sei Yap" OR "Sze Yap" OR SzeYap OR Siyi OR "Si Yi" OR Seiyap) -is:retweet (lang:en OR lang:zh-TW OR lang:zh OR lang:und) -is:reply',
         "tag": 'Sze Yap'},
        {"value": '(Taishanhua OR Toisanwa OR Toisaanwaa OR Taicheng OR Toishan OR Taishanese OR Taishan OR Toisan OR Toisanese OR Toishanese) -is:retweet (lang:en OR lang:zh-TW OR lang:zh OR lang:und) -is:reply',
         "tag": 'Taishan'},
        {"value": '(Hoisanese OR "Hoisan Sauce" OR "Hoisin Sauce" OR Hoisanva OR Hoisiang OR Hoisan) -is:retweet (lang:en OR lang:zh-TW OR lang:zh OR lang:und) -is:reply',
         "tag": 'Hoisan'},
        {"value": '(Hiak OR "Hiak Fan" OR "Hek Fan") -is:retweet (lang:en OR lang:zh-TW OR lang:zh OR lang:und) -is:reply',
         "tag": 'Hiak Fan'},
        {"value": '"Taishan Sauce" -is:retweet (lang:en OR lang:zh-TW OR lang:zh OR lang:und) -is:reply',
         "tag": 'Taishan Sauce'},
    ]
    headers = create_headers(BEARER_TOKEN)
    curr_rules = get_rules(headers)
    if sorted([rule['value'] for rule in rules]) != sorted(list(map(lambda rule: rule['value'], curr_rules.setdefault('data', [])))):
        print("Rules changed, updating...")
        if len(curr_rules['data']) > 0:
            delete_all_rules(headers, curr_rules)
        set_rules(headers, rules)
    else:
        print("Rules Unchanged")
    while True:
        try:
            print('Stream Started')
            get_stream(headers)
        except KeyboardInterrupt:
            exit()
        except TooManyConnections:
            print("\nToo Many Connections, retrying in 60 seconds...")
            time.sleep(60)
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError) as err:
            print(err)
            print(f'\n{datetime.now().strftime("%x %X")}: Put to sleep before retrying...')
            time.sleep(100)
            continue
        except Exception as exc:
            print (traceback.format_exc())
            print (exc)
            print(f'\n{datetime.now().strftime("%x %X")} darn, got an error')
            time.sleep(100)

start_webhook()