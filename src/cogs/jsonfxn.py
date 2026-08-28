import json
import codecs
from os.path import dirname
from discord import channel
from data_paths import cog_file

filepath = dirname(__file__)


def _default_datajson() -> dict:
    return {
        'system': {
            'dm_msg': (
                "Hi there {user}! Thanks for checking out "
                "my dm functionality! Please be aware that this channel is still "
                "being monitored by me {pigpig} (and only me, no one else has "
                "access) to prevent abuse/misuse and to catch those pesky bugs! If "
                "you do not want me to see this chat just type a message here saying "
                "so! Otherwise, thanks for using Sze Yap Bot!"
            ),
            'igonored_dms': [],
            'youtube': [],
            'youtube_count': 0,
        }
    }

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


def open_datajson(guild_id: int):
    guild_id = str(guild_id)
    data_path = cog_file('data.json')
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = _default_datajson()
        save_json(data_path, data)
    if guild_id not in data:
        data[guild_id] = {
            'command_count': {
                'sl': {}, 
                'gc': {}, 
                'penyim': {}, 
                'leave_channel': {},
                'audio': {}
            },
            'roles': {},
        }
        data.setdefault('system', _default_datajson()['system'])
        save_json(data_path, data)
    return data

def get_prefix(client, message):
    prefix_path = cog_file('prefixes.json')
    try:
        with open(prefix_path, 'r', encoding='utf-8') as f:
            prefixes = json.load(f)
    except FileNotFoundError:
        prefixes = {}
        save_json(prefix_path, prefixes)
    if isinstance(message.channel, channel.DMChannel):
        return '+'
    try:
        return prefixes[str(message.guild.id)]
    except KeyError:
        prefixes[str(message.guild.id)] = '+'
        save_json(prefix_path, prefixes)
        return '+'