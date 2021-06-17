import discord
from discord.ext import commands
from discord.utils import get
from discord.player import FFmpegPCMAudio
from os.path import join, dirname
from asyncio import sleep
from PIL import Image, ImageDraw, ImageFont, ImageSequence
from textwrap import wrap
import io
from cogs.jsonfxn import open_datajson, save_json

path = dirname(__file__)

async def play_egg(self, ctx, type_: str):
    if type_ == 'gummybear':
        file = join(path, 'easter_eggs', 'gummy_bear.mp3')
    elif type_ == 'pig':
        file = join(path, 'easter_eggs', 'pig.mp3')
    elif type_ == 'meow':
        file = join(path, 'easter_eggs', 'meow.mp3')
    
    if not ctx.author.voice:
        return
    channel = ctx.author.voice.channel
    voice = get(self.client.voice_clients, guild=ctx.guild)
    
    if voice is not None:
        if voice.channel != ctx.author.voice.channel:
            voice = await voice.move_to(ctx.author.voice.channel)
    else:
        permissions = channel.permissions_for(ctx.guild.me)
        if permissions.connect:
            voice = await channel.connect()
        else:
            permissions = ctx.channel.permissions_for(ctx.guild.me)
            if permissions.send_messages:
                await ctx.send("Sorry, I can't seem to connect to the vc")
            else:
                await ctx.author.send(
                    "Sorry, I can't seem to connect to the vc "
                    f"or even type in ur channel! "
                    f"What kind of permissions are these?")
            return

    source = FFmpegPCMAudio(file)
    voice.play(source)
    
    
    guild_id = str(ctx.guild.id)
    data = open_datajson(ctx.guild.id)
    
    data[guild_id]['easter_egg'][str(ctx.author.id)][type_] = \
        data[guild_id].setdefault('easter_egg', {})\
            .setdefault(str(ctx.author.id), {}).setdefault(type_, 0) + 1
    save_json(join(path, 'data.json'), data)
    egg_num = 3
    if len(data[guild_id]['easter_egg'][str(ctx.author.id)].keys()) == egg_num:
        data[guild_id]['easter_egg'][str(ctx.author.id)]['found_all'] = True
        save_json(join(path, 'data.json'), data)
        
        text = f"Congrats {ctx.author.mention}! You found all {egg_num} "\
        f"easter eggs!"
        file = discord.File(join(path, '..', 'pictures', 'celebration.gif'))
        await ctx.author.send(content=text, file=file)
    await sleep(8)
    await voice.disconnect()

class EasterEgg(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command()
    async def gummybear(self, ctx):
        await play_egg(self, ctx, 'gummybear')
        
    @commands.command()
    async def pig(self, ctx):
        await play_egg(self, ctx, 'pig')
        
    @commands.command()
    async def meow(self, ctx):
        await play_egg(self, ctx, 'meow')
        

def setup(client):
    client.add_cog(EasterEgg(client))
        




