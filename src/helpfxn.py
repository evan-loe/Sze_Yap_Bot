import discord
from embed import EmbedList
import json
from os.path import join, dirname, realpath
import sys

__location__ = realpath(join(sys.path[0], dirname(__file__)))

def create_help_embed(prefix: str='+', version: str='main_help') -> EmbedList:
    embed_list = EmbedList(message_id=None, type_id=7)
    
    with open(join(__location__, 'help.json'), 'r') as f:
        helpdict = json.load(f)[version]
    
    for page in helpdict:
        page = helpdict[page]
        embed = discord.Embed(
            title=page['title'],
            colour=discord.Color.from_rgb(*page['colour']))
        embed.add_field(
            name=page['name'].format(prefix=prefix),
            value=page['value'].format(prefix=prefix))
        embed_list.add_page(embed, [], [])
    return embed_list