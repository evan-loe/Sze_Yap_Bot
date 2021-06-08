import discord
from discord.errors import HTTPException
from discord.ext import commands
from cogs.jsonfxn import open_datajson, save_json
from os.path import join, dirname
from embed import add_to_master, page_num
import traceback
import sys
import asyncio

from embed import EmbedList


data_path = join(dirname(__file__), 'data.json')


class CustomRoles(commands.Cog):
    
    def __init__(self, client):
        self.client = client
    
    @commands.has_permissions(administrator=True)
    @commands.group(name='rolepage', invoke_without_command=True)
    async def rolepage(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Subcommands are 'pages', 'send', 'add', and 'remove'")

    @commands.has_permissions(administrator=True)
    @rolepage.command(name='pages')
    async def pages_sub(self, ctx):
        guild_id = str(ctx.guild.id)
        pages = open_datajson(data_path, ctx.guild.id)[guild_id]['roles']
        if len(pages) == 0:
            await ctx.send("There are no role pages for this server!")
            return
        emoji_list = []
        embed_list = EmbedList(None, 9)
        for page in pages.items():
            desc_page = []
            page_emojis = []
            for role in page[1]['e_list']:
                server_role = ctx.guild.get_role(role[0])
                emoji = role[1]
                if type(role[1]) != str:
                    emoji = await ctx.guild.fetch_emoji(role[1])
                desc_page.append(f'Select {emoji} for {server_role}')
                page_emojis.append(emoji)
                    
            emoji_list.append(page_emojis)
            embed = discord.Embed(title=page[0], description="\n".join(desc_page))
            embed_list.add_page(embed=embed, audio=[], link=[])
        sent_embed = await ctx.send(
            content=f'Displaying all role pages for {ctx.guild.name}',
            embed=page_num(embed_list).first_page())
        add_to_master(embed_list, sent_embed)
        await sent_embed.add_reaction('⬅️')
        await sent_embed.add_reaction('➡️')
        
    @commands.has_permissions(administrator=True)
    @rolepage.command(name='send', aliases=['display'])
    async def send_sub(self, ctx, channel: discord.TextChannel, *, page_name):
        guild_id = str(ctx.guild.id)
        data = open_datajson(data_path, ctx.guild.id)
        pages = data[guild_id]['roles']
        if page_name.isdigit():
            title, role_page = list(pages.items())[int(page_name)-1]
        else:
            try:
                role_page = pages[page_name]
                title = page_name
            except KeyError:
                await ctx.send("Sorry, I couldn't find that")
                return
        
        desc_page = []
        page_emojis = []
        for role in role_page['e_list']:
            server_role = ctx.guild.get_role(role[0])
            emoji = role[1]
            if type(role[1]) != str:
                emoji = await ctx.guild.fetch_emoji(role[1])
            desc_page.append(f'Select {emoji} for {server_role}')
            page_emojis.append(emoji)

        embed = discord.Embed(title=title, description = "\n".join(desc_page))
        sent_embed = await channel.send(embed=embed)
        for react in page_emojis:
            await sent_embed.add_reaction(react)
        
        data[guild_id].setdefault('role_msg_ids', []).append(sent_embed.id)
        data[guild_id]['roles'][title]['msg_id'] = sent_embed.id
        
        save_json(data_path, data)
    
    @commands.has_permissions(administrator=True)
    @rolepage.command(name='allroles')
    async def allroles(self, ctx):
        def check(reaction, user):
            return reaction.message == sent_message
        def check_msg(message):
            return message.author == ctx.author
        try:
            guild_id = str(ctx.guild.id)
            sent_message = await ctx.send(
                'React to this message with the emoji you want to use!')
            reaction, user = await self.client.wait_for(
                'reaction_add', timeout=60, check=check)
            data = open_datajson(data_path, guild_id)
            data[guild_id].setdefault('all_roles', {}).setdefault('emoji', "")
            if type(reaction.emoji) == str:
                emoji = reaction.emoji
            else:
                emoji = reaction.emoji.id
            data[guild_id]['all_roles']['emoji'] = emoji
            sent_message = await ctx.send("What is the title?")
            title = await self.client.wait_for(
                'message', timeout=60, check=check_msg)
            data[guild_id]['all_roles']['title'] = title.content
            
            sent_message = await ctx.send("What is the description?")
            description = await self.client.wait_for(
                'message', timeout=60, check=check_msg)
            data[guild_id]['all_roles']['description'] = description.content
            save_json(data_path, data)
        except asyncio.TimeoutError:
            await ctx.send('Sorry I timed out. Please enter more quickly next time!')
        await ctx.send("Ok, I configured the allroles message. Use `send_allroles` to send it!")
    
    @commands.has_permissions(administrator=True) 
    @rolepage.command(name='send_allroles')
    async def send_allroles(self, ctx, channel: discord.TextChannel):
        if not isinstance(channel, discord.TextChannel):
            await ctx.send('Please provide a proper text channel')
            return
        guild_id = str(ctx.guild.id)
        try:
            data = open_datajson(data_path, guild_id)
            title = data[guild_id]['all_roles']['title']
            description = data[guild_id]['all_roles']['description']
        except KeyError:
            await ctx.send("Sorry, there's nothing configured for the all roles role message. Please use the `allroles` command")
            return
        
        embed =  discord.Embed(
            title=title, description=description)
        sent_embed = await channel.send(embed=embed)
        if type(data[guild_id]['all_roles']['emoji']) != str:
            emoji = await ctx.guild.fetch_emoji(data[guild_id]['all_roles']['emoji'])
        else:
            emoji = data[guild_id]['all_roles']['emoji']
        await sent_embed.add_reaction(emoji)
        data[guild_id]['role_msg_ids'].append(sent_embed.id)
        description = data[guild_id]['all_roles']['msg_id'] = sent_embed.id
        save_json(data_path, data)
        

    @commands.has_permissions(administrator=True)
    @rolepage.command(name='add')
    async def add_sub(self, ctx, role: discord.Role, *, page_name):
        def check(reaction, user):
            return reaction.message == sent_message

        def check_msg(message):
            return message.author == ctx.author

        data = open_datajson(data_path, ctx.guild.id)
        guild_id = str(ctx.guild.id)
        if 'roles' not in data[guild_id].keys():
            data[guild_id]['roles'] = {}
        if page_name not in data[guild_id]['roles']:
            data[guild_id]['roles'][page_name] = {
                'e_list': [], 
                'msg_id': 0, 
                'all_e': ''
            }
        sent_message = await ctx.send("Please react to this message with the emoji you want")
        reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=check)
        emoji = reaction.emoji
        
        
        await ctx.send(f"Ok, I added a role to the page ***{page_name}***. Use the `send` command to send it!\nReact to this message with any emoji if you want to add a custom description!")
        reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=check)
        await ctx.send("What is the custom message you want?")
        message = None
        # add try except for timeout
        message = await self.client.wait_for('message', timeout=60, check=check_msg)
        if isinstance(emoji, discord.Emoji):
            if not reaction.emoji.is_usable() and not reaction.emoji.available:
                await ctx.send("Sorry, I can't seem to use that emoji")
                return
            data[guild_id]['roles'][page_name]['e_list'].append((role.id, emoji.id, message))
        else:
            data[guild_id]['roles'][page_name]['e_list'].append((role.id, emoji, message))
        save_json(data_path, data)
        
        
    @commands.has_permissions(administrator=True)
    @rolepage.group(name='remove', invoke_without_command=True)
    async def remove(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Subcommands for remove are 'page' and 'role' ")

    @commands.has_permissions(administrator=True)
    @remove.command(name='page')
    async def removepage_sub(self, ctx, *, page_name):
        data = open_datajson(data_path, ctx.guild.id)
        if data[str(ctx.guild.id)]['roles'].pop(page_name, None) is None:
            await ctx.send("Sorry, couldn't find that page")
            return
        else:
            await ctx.send(f"Ok, I removed the ***{page_name}*** page")
        save_json(data_path, data)

    @commands.has_permissions(administrator=True)
    @remove.command(name='role')
    async def removerole_sub(self, ctx, d_role:discord.Role, *, page_name):
        data = open_datajson(data_path, ctx.guild.id)
        try:
            for index, role in enumerate(data[str(ctx.guild.id)]['roles'][page_name]['e_list']):
                if role[0] == d_role.id:
                    data[str(ctx.guild.id)]['roles'][page_name]['e_list'].pop(index)
                    await ctx.send(
                        f"Ok, I removed the ***{d_role}*** role from the page "
                        f"***{page_name}***")
                    if len(data[str(ctx.guild.id)]['roles'][page_name]['e_list']) == 0:
                        data[str(ctx.guild.id)]['roles'].pop(page_name, None)
                    save_json(data_path, data)
                    return
            else:
                await ctx.send("Sorry, couldn't find that role")
        except:
            await ctx.send("Sorry, couldn't find that page")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            if payload.guild_id is None or payload.member.bot:
                return
        except AttributeError:
            return
        guild_id = str(payload.guild_id)
        data = open_datajson(data_path, guild_id)[guild_id]
        if payload.message_id not in data.setdefault('role_msg_ids', []):
            return
        emoji = payload.emoji
        if emoji.is_custom_emoji():
            emoji = emoji.id
        else:
            emoji = emoji.name
        add_all = False
        try:
            all_emoji = data['all_roles']['emoji']
            if all_emoji == emoji and data['all_roles']['msg_id'] == payload.message_id:
                add_all = True
        except KeyError:
            pass
        finally:
            for page in data['roles'].values():
                if page['msg_id'] != payload.message_id and not add_all:
                    continue
                for role in page['e_list']:
                    if role[1] == emoji or add_all:
                        role_to_add = self.client.get_guild(
                            payload.guild_id).get_role(role[0])
                        await payload.member.add_roles(role_to_add,
                            reason=f"{payload.member} reacted to my message",
                            atomic=True)


    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        guild_id = str(payload.guild_id)
        message_id = payload.message_id
        data = open_datajson(data_path, guild_id)
        if message_id in data[guild_id].setdefault('role_msg_ids', []):
            data[guild_id]['role_msg_ids'].remove(message_id)
            save_json(data_path, data)
    
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.guild_id is None or payload.member.bot:
            return
        guild_id = str(payload.guild_id)
        guild = self.client.get_guild(int(guild_id))
        member = await guild.fetch_member(payload.user_id)
        
        data = open_datajson(data_path, guild_id)[guild_id]
        if payload.message_id not in data.setdefault('role_msg_ids', []):
            return
        emoji = payload.emoji
        if emoji.is_custom_emoji():
            emoji = emoji.id
        else:
            emoji = emoji.name
        add_all = False
        try:
            all_emoji = data['all_roles']['emoji']
            if all_emoji == emoji and data['all_roles']['msg_id'] == payload.message_id:
                add_all = True
        except KeyError:
            pass
        finally:
            for page in data['roles'].values():
                if page['msg_id'] != payload.message_id and not add_all:
                    continue
                for role in page['e_list']:
                    if role[1] == emoji or add_all:
                        role_to_add = self.client.get_guild(
                            payload.guild_id).get_role(role[0])
                        await payload.member.add_roles(role_to_add,
                            reason=f"{payload.member} reacted to my message",
                            atomic=True)
                        

    # @rolepage.error
    # @add_sub.error
    # @send_sub.error
    # @pages_sub.error
    # @removepage_sub.error
    # @removerole_sub.error
    # @send_allroles.error
    # async def role_error(self, ctx, error):
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         await ctx.send(
    #             f'Please include the "{error.param.name}" option!')
    #     elif isinstance(error, commands.CommandInvokeError):
    #         await ctx.send("Sorry, there was an issue. Maybe something isn't configured properly for this guild?")
    #     elif isinstance(error, commands.MissingPermissions):
    #         await ctx.send("Sorry, you're missing the permissions to use this command") 
    #     else:
    #         print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    #         traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    
    
def setup(client):
    client.add_cog(CustomRoles(client))

        
        
