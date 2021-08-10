from embed import EmbedList, add_to_master, page_num
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
        data = open_datajson(guild_id)[str(ctx.guild.id)]['command_count']
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
        
        data = open_datajson(guild_id)
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
    
    @commands.group(name='servers', invoke_without_command=True)
    async def servers(self, ctx):
        if ctx.author.id != 693267245610303518:
            return
        embed_list = EmbedList(message_id=None, type_id=8)
        guild_list = self.client.guilds
        guild_num = len(self.client.guilds)
        while len(guild_list) > 0:
            embed = discord.Embed(title=f"Servers - ({guild_num})")
            embed.description = "\n".join([f"**{server.name}** - `{str(server.id)}`" for server in guild_list[:20]])
            guild_list = guild_list[20:]
            embed_list.add_page(embed, [], [])
        sent_embed = await ctx.send(embed=page_num(embed_list).first_page())
        add_to_master(embed_list, sent_embed)
        for emoji in emoji_list[:2]:
            await sent_embed.add_reaction(emoji)
        
        
    @servers.command(name='detail', aliases=['details', 'info'])
    async def detail_server(self, ctx):
        if ctx.author.id != 693267245610303518:
            return
        embed_list = EmbedList(message_id=None, type_id=8)
        for server in self.client.guilds:
            # server = self.client.fetch_guild(guild.id)
            embed = discord.Embed(
                title=server.name,
                description=f"`id:` {server.id}\n`Member Count:` **{server.member_count}**\n`Owner:` {server.owner}\n`Boosts:` {server.premium_subscription_count}")
            if server.description:
                embed.description += f"\n`Description:` {server.description}"
            
            if server.features:
                embed.description += f"\n`Features:` {', '.join(server.features)}"
            else:
                embed.description += f"\n`Features:` None"
            if server.icon_url:
                embed.set_thumbnail(url=server.icon_url)
            channels_text = f"\n`Channels:`\n{', '.join([chan.name for chan in server.text_channels[:20]])}"
            if len(server.text_channels):
                channels_text += f"***and {len(server.text_channels) - 20} more***"
            embed.description += channels_text
            if server.member_count > 20:
                embed.description += f"\n`Members:`\n{', '.join(str(member) for member in server.members[:20])} ***and {server.member_count - 20} more***"
            else:
                embed.description += f"\n`Members:`\n{', '.join(str(member) for member in server.members)}"
            embed_list.add_page(embed, [], [])
        sent_embed = await ctx.send(embed=page_num(embed_list).first_page())
        add_to_master(embed_list, sent_embed)
        for emoji in emoji_list[:2]:
            await sent_embed.add_reaction(emoji)



def setup(client):
    client.add_cog(CommandCount(client))