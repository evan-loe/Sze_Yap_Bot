from discord import webhook
from discord.ext import commands
from os.path import join, dirname

from cogs.jsonfxn import open_datajson, save_json


class MediaWebhooks(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.has_permissions(administrator=True)
    @commands.group(name='webhook', invoke_without_command=True)
    async def webhook(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Webhooks you can add include Twitter and Youtube")
    
    
    @commands.has_permissions(administrator=True)
    @webhook.command(name='twitter')
    async def twitter(self, ctx, link: str=None):
        if link is None:
            await ctx.send("Please copy the link of the webhook you wish to add and include that in the command! Make sure to keep the link secret!")
            return
        data = open_datajson(ctx.guild.id)
        if link not in data['system']['twitter']:
            data['system']['twitter'].append(link)
            save_json(join(dirname(__file__), 'data.json'), data)
            await ctx.send("Ok, I added that webhook to my list. You'll start receiving tweets soon!")
        else:
            await ctx.send("I already have that webhook on file!") 
    
    @commands.has_permissions(administrator=True)
    @webhook.command(name='youtube')
    async def youtube(self, ctx, link: str=None):
        if link is None:
            await ctx.send("Please copy the link of the webhook you wish to add and include that in the command! Make sure to keep the link secret!")
            return
        data = open_datajson(ctx.guild.id)
        if link not in data['system']['youtube']:
            data['system']['youtube'].append(link)
            save_json(join(dirname(__file__), 'data.json'), data)
            await ctx.send("Ok, I added that webhook to my list. You'll start receiving youtube videos soon!")
        else:
            await ctx.send("I already have that webhook on file!")
    
    @commands.has_permissions(administrator=True)
    @webhook.command(name='remove')
    async def remove(self, ctx, link: str=None):
        if link is None:
            await ctx.send("Please copy the link of the webhook you wish to remove and include that in the command! Make sure to keep the link secret!")
            return
        data = open_datajson(ctx.guild.id)
        if link in data['system']['twitter']:
            data['system']['twitter'].remove(link)
        elif link in data['system']['youtube']:
            data['system']['youtube'].remove(link)
        else:
            await ctx.send("Sorry, I couldn't find that link in my list")
        save_json(join(dirname(__file__), 'data.json'), data)
        
        
def setup(client):
    client.add_cog(MediaWebhooks(client))
    