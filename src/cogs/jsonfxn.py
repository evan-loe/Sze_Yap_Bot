import json
import codecs
from os.path import join, dirname
from discord import channel

filepath = dirname(__file__)

def save_json(path: str, json_file: dict):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(json_file, f, indent=4, ensure_ascii=False)


def open_wcjson(path: str, guild_id: int):
    with codecs.open(path, 'r', encoding='utf-8') as f:
        json_file = json.load(f)
    if str(guild_id) not in json_file.keys():
        json_file[str(guild_id)] = {
            "showwcmsg": False,
            "en_title": "", 
            "ch_title": "",
            "pfp": True, 
            "message": "",
            "channel": None, 
            "hoisan_pics": False,
            "text_colour": [255, 255, 255]
        }
        save_json(path, json_file)
    return json_file


def open_datajson(path: str, guild_id: int):
    guild_id = str(guild_id)
    with open(path, 'r') as f:
        data = json.load(f)
    if guild_id not in data:
        data[guild_id] = {
            'command_count': {
                'sl': {}, 
                'gc': {}, 
                'penyim': {}, 
                'leave_channel': {},
                'audio': {}
            }
        }
        save_json(path, data)
    return data

def get_prefix(client, message):
    prefix_path = join(filepath, 'prefixes.json')
    with open(prefix_path, 'r') as f:
        prefixes = json.load(f)
        if isinstance(message.channel, channel.DMChannel):
            return '+'
        else:
            try:
                # return prefixes[str(message.guild.id)]
                return '/'
            except KeyError:
                prefixes[str(message.guild.id)] = '+'
                save_json(prefix_path, prefixes)