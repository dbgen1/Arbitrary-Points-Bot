import discord
from discord.ext import commands
from discord.utils import get
import os
import json


class Customization(commands.Cog):    
    def __init__(self, client):
        self.client = client
        self.path = os.getcwd()
        with open(f"{self.path}/config.json") as f:
            self.config = json.load(f)
            self.prefix = self.config["prefix"]
            self.commandRole = self.config["commandRole"]
            self.username = self.config["username"]

    async def cog_check(self, ctx):
        hasRole = get(ctx.guild.roles, name=f"{self.commandRole}")
        if not hasRole in ctx.author.roles:
            await ctx.send("You do not have permissions to run this command.")
        return hasRole in ctx.author.roles

    @commands.command()
    async def prefix(self, ctx, prefix):
        mode = "prefix"
        self.updateConfig(mode, prefix)
        await ctx.send("Prefix updated.")

    @commands.command()
    async def username(self, ctx, *args):
        name = " ".join(args[:])
        mode = "username"
        self.updateConfig(mode, name)
        await self.client.user.edit(username = name)
        await ctx.send("Username updated.")

    @commands.command()
    async def status(self, ctx, *args):
        status = " ".join(args[:])        
        mode = "status"
        self.updateConfig(mode, status)
        await self.client.change_presence(activity=discord.Game(f'{status}'))
        await ctx.send("Status updated.")

    @commands.command()
    async def commandRole(self, ctx, *args):
        role = " ".join(args[:])        
        mode = "commandRole"
        self.updateConfig(mode, role)
        await ctx.send("Restart required. :warning: Make sure everything is correct before restarting or you may lose access to admin commands.")

    def updateConfig(self, mode, new):
        with open(f'{self.path}/config.json', 'r') as f:
            self.config = json.load(f)
        self.config[f"{mode}"] = new
        with open(f'{self.path}/config.json', 'w') as f:
            json.dump(self.config, f, indent = 4)


def setup(client):
    client.add_cog(Customization(client))