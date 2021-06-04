from embed import EmbedList, add_to_master
from discord.ext import commands
import discord
from os.path import join, dirname, realpath
from cogs.jsonfxn import open_datajson, save_json
import sys

emoji_list = ('⬅️', '➡️', '🔊', '⬇️', '⬆️', '📚')
__location__ = realpath(join(sys.path[0], dirname(__file__)))
class CommandCount(commands.Cog):
    
    def __init__(self, client):
        self.client = client
    
    @commands.command()
    async def count(self, ctx):
        embed_list = EmbedList(message_id=None, type_id=8)
        if isinstance(ctx.channel, discord.DMChannel):
            guild_id = 'dm'
        else:
            guild_id = str(ctx.guild.id)
        data = open_datajson(join(__location__, 'data.json'), guild_id)[str(ctx.guild.id)]['command_count']
        try:
            for command in data.items():
                text = f'***{command[0]}***\n```'
                for channel in command[1].items():
                    if ctx.guild is not None or ctx.channel.id == int(channel[0]):
                        text += f'{self.client.get_channel(int(channel[0])).name} -'\
                            f' {channel[1]}\n'
                embed = discord.Embed(
                    title=f"Commands for {ctx.guild.name}",
                    description=text + '```')
                embed_list.add_page(embed, audio=[], link=[])
        except KeyError:
            return
        sent_embed = await ctx.send(embed=embed_list.first_page())
        add_to_master(embed_list, sent_embed)
        for emoji in emoji_list[:2]:
            await sent_embed.add_reaction(emoji)


    @commands.Cog.listener()
    async def on_command(self, ctx):
        channel = ctx.channel
        if channel is None:
            return
        elif isinstance(channel, discord.DMChannel):
            guild_id = "dm"
        else:
            guild_id = str(ctx.guild.id)
        channel_id = str(channel.id)
        command = ctx.command.name
        
        data = open_datajson(join(__location__, 'data.json'), guild_id)
        com_count = data[guild_id]['command_count']
        try:
            if command not in com_count:
                com_count[command] = {}
            if channel_id not in com_count[command]:
                com_count[command][channel_id] = 1
            else:
                com_count[command][channel_id] += 1

        except KeyError:
            return

        data[guild_id]['command_count'] = com_count
        save_json(join(__location__, 'data.json'), data)



def setup(client):
    client.add_cog(CommandCount(client))