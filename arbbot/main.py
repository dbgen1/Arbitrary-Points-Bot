import discord
from discord.ext import commands
import sqlite3
import json
import re
import os
import sys

with open("config.json") as f:
    config = json.load(f)
    prefix = config["prefix"]
    TOKEN = config["TOKEN"]
    commandRole = config["commandRole"]
    status = config["status"]

def getPrefix(client, message):
    with open("config.json") as f:
        config = json.load(f)
        prefix = config["prefix"]
    return prefix

client = commands.Bot(command_prefix = getPrefix)
client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(f'{status}'))  
    print('Logged in.')


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You are missing arguments in your command.', delete_after = 2)
    elif isinstance(error, (commands.MissingPermissions, commands.MissingRole)):
        await ctx.send("You do not have the appropriate permissions to run this command.", delete_after = 2)


@client.command()
@commands.has_role(f"{commandRole}")
async def points(ctx, operation, member: discord.Member, value):
    memberID = member.id
    value = int(value)

    db = sqlite3.connect('pointdata.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT points FROM pointdata WHERE member = {memberID}")
    result = cursor.fetchone()

    if (operation != "add" and operation != "remove"):
        await ctx.send("Invalid operation. Please use `add` or `remove`.", delete_after = 2)
        return

    if result is None:
        sql = ("INSERT INTO pointdata(member, points, nickname) VALUES(?,?,?)")
        values = registerUser(memberID, value, operation)
        await ctx.send(f"Changed <@{memberID}>'s points by {value}.")

    elif operation == "add":
        newValue = result[0] + value
        sql = ("UPDATE pointdata SET points = ? WHERE member = ?")
        values = (newValue, memberID)
        await ctx.send(f"Gave {value} points to <@!{memberID}>. They now have {newValue} points.")

    elif operation == "remove":
        newValue = result[0] - value
        sql = ("UPDATE pointdata SET points = ? WHERE member = ?")
        values = (newValue, memberID)
        await ctx.send(f"Removed {value} points to <@!{memberID}>. They now have {newValue} points.")

    cursor.execute(sql, values)
    db.commit()
    cursor.execute(f"SELECT nickname FROM pointdata WHERE member = {memberID}")
    result = cursor.fetchone()
    if result[0] == 1:
        print("in if")
        newnick = changeNick(member, True)
        print(f"newnick is {newnick}")
        await member.edit(nick=newnick)
        print("changed")
    cursor.close()
    db.close()
    

@client.command()
@commands.has_role(f'{commandRole}')
async def sql(ctx, *args):
    db = sqlite3.connect('pointdata.sqlite')
    cursor = db.cursor()
    cursor.execute(" ".join(args[:]))
    await ctx.send("Operation completed Successfully.")
    db.commit()
    cursor.close()
    db.close()


@client.command()
async def nick(ctx):
    member = ctx.message.author
    print(type(member))
    memberID = member.id 
    db = sqlite3.connect('pointdata.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT nickname FROM pointdata WHERE member = {memberID}")
    result = cursor.fetchone()

    if result is None:
        sql = ("INSERT INTO pointdata(member, points, nickname) VALUES(?,?,?)")
        values = registerUser(memberID, 0)
        cursor.execute(sql, values)
        await ctx.send("Nickname feature enabled.")
        db.commit()
        nickname = True

    elif result[0] == 0:
        sql = (f"UPDATE pointdata SET nickname = ? WHERE member = ?")
        values = (1, memberID)
        cursor.execute(sql, values)
        await ctx.send("Nickname feature enabled.")
        db.commit()
        nickname = True

    elif result[0] == 1:
        sql = (f"UPDATE pointdata SET nickname = ? WHERE member = ?")
        values = (0, memberID)
        cursor.execute(sql, values)
        db.commit()
        await ctx.send("Nickname feature disabled.")
        nickname = False
    
    cursor.close()
    db.close()
    newnick = changeNick(member, nickname)
    await member.edit(nick=newnick)

@client.command()
async def balance(ctx):
    memberID = ctx.message.author.id
    db = sqlite3.connect('pointdata.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT points FROM pointdata WHERE member = {memberID}")
    result = cursor.fetchone()

    if result is None:
        await ctx.send("You have 0 points.")
    else:
        await ctx.send(f"You have {result[0]} points.")
    cursor.close()
    db.close()



@client.command(pass_context = True)
async def help(ctx):
    member = ctx.message.author
    embed = discord.Embed(color = discord.Colour.orange())
    embed.set_author(name='Help')

    embed.add_field(name='!help', value = 'Shows this message.', inline = False)
    embed.add_field(name='!nick', value = 'Toggles the point nicknames.', inline = False)
    embed.add_field(name='!balance', value = 'Tells you how many points you have.', inline = False)
    embed.add_field(name='!points', value = 'Admin only: !points <add|remove> <user> <amount>', inline = False)
    embed.add_field(name='!sql', value = 'Admin only: Direct database manipulation. USE WITH CAUTION!', inline = False)
    embed.add_field(name='!prefix', value = 'Admin only: !prefix <new prefix>', inline = False)
    embed.add_field(name='!status', value = 'Admin only: !status <new status>.', inline = False)
    embed.add_field(name='!username', value = 'Admin only: !username <new username> (can only be used twice in an hour).', inline = False)

    await ctx.send(embed=embed)
    


def registerUser(memberID, value, operation = None):
    if operation == "add":
        values = (memberID, value, 0)
    elif operation == "remove":
        values = (memberID, 0-value, 0)
    else:
        values = (memberID, value, 1)

    return(values)


def changeNick(member, nickname):
    memberID = member.id
    db = sqlite3.connect('pointdata.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT points FROM pointdata WHERE member = {memberID}")
    result = cursor.fetchone()
    if nickname:
        nick = f"{member.name} - {result[0]} points"
    else:
        nick = None
    cursor.close()
    db.close()

    return(nick)

for f in os.listdir('./cogs'):
    if f.endswith('.py'):
        client.load_extension(f'cogs.{f[:-3]}')



client.run(TOKEN)