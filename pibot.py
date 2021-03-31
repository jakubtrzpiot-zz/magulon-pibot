import discord
import ffmpeg
import time
import json
import random
import asyncio
import numpy as np
from discord.ext import commands
with open("config.json", "r") as json_config:
    config = json.load(json_config)

# *****STATICS*****
intents = discord.Intents.default()
intents.members = True

song = config["song"]
TOKEN = config["TOKEN"]
description = config["description"]

bot = commands.Bot(
    command_prefix=".",
    description=description,
    guild_subscriptions=True,
    intents=intents,
)

# *****BOT INITIALIZATION*****
@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online, activity=discord.Game("🧅💩💩🧅")
    )
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

bot.deathroll_enabled = False
bot.deathroll_channel = None
bot.bot_channel = None

@bot.event
async def on_member_join(member):
    msg = "Siema " + mention + "! Wpisz help zeby sprawdzic liste komend"
    await ctx.send(msg)

def isConnected(ctx):
    return ctx.voice_client

async def on_deathroll(rand: int, looser: discord.User):
    if rand == 1:
        msg = "🔫" + looser.mention + " przegrywa death roll!🔫"
        await bot.bot_channel.send(msg)
        return_link = "Wróć na kanał " + bot.bot_channel.mention
        await bot.deathroll_channel.send(return_link)
        time.sleep(5)
        await bot.deathroll_channel.delete()
        print("pre" + bot.bot_channel)
        bot.deathroll_enabled = False
        bot.deathroll_channel = None
        bot.bot_channel = None
        print("post" + bot.bot_channel)
    else:
        pass

# *****TEXT CHANNEL COMMANDS*****
@bot.command()
async def status(ctx, botStatus: str = None, botActivity: str = ""):
    states = {
        "online": discord.Status.online,
        "offline": discord.Status.offline,
        "invisible": discord.Status.invisible,
        "idle": discord.Status.idle,
        "dnd": discord.Status.do_not_disturb,
    }
    if botStatus == "reset":
        await bot.change_presence(
            status=discord.Status.online, activity=discord.Game("🧅💩💩🧅")
        )
        await ctx.send("Status has been reset!")
    elif botStatus == None:
        await ctx.send("Dostępne statusy: ")
        await ctx.send(states.keys())
    else:
        setStatus = states.get(botStatus, discord.Status.online)
        setActivity = discord.Game(botActivity)
        await bot.change_presence(status=setStatus, activity=setActivity)
        if botStatus == "dnd":
            botStatus = "do not disturb"
        statusMsg = "Changed status to " + botStatus + "!"
        activityMsg = "Changed activity to " + botActivity + "!"
        await ctx.send(statusMsg)
        if botActivity != "":
            await ctx.send(activityMsg)

@bot.command()
async def members(ctx, guildid: int = None):
    server = bot.get_guild(guildid)
    title = "Id członków serwera " + server.name
    embed = discord.Embed(title=title)
    for member in bot.get_all_members():
        if member.guild.id == guildid:
            msg = member.display_name + " - " + str(member.id)
            embed.add_field(name=member.display_name, value=member.id)
    await ctx.send(embed=embed)

@bot.command()
async def usun(ctx, passtype: str, passid: int = None):
    if passid == None:
        await ctx.send("Wpisz poprawne id")
    elif passtype == "kanal":
        channel = bot.get_channel(passid)
        await channel.delete()
    elif passtype == "wiadomosc":
        msg = await ctx.channel.fetch_message(passid)
        await msg.delete()
    else:
        await ctx.send("Podaj poprawny typ")

@bot.command()
async def roll(ctx, number: int = None):
    if isinstance(number, int):
        author = ctx.author
        rand = random.randint(1, number)
        await ctx.send(rand)
        if bot.deathroll_enabled == True:
            await on_deathroll(rand, author)
    else:
        await ctx.send("Podaj prawidłową liczbę")

@bot.command()
async def deathroll(ctx, competitor: discord.User = None):
    author = ctx.author
    if isinstance(competitor, discord.User) and bot.deathroll_enabled == False:
        if not author == competitor:
            msg = competitor.mention + " Czy zgadzasz się na death roll?"
            accept_decline = await ctx.send(msg)
            await accept_decline.add_reaction("✅")

            def check(reaction, user):
                return user == competitor and str(reaction.emoji) == "✅"

            try:
                reaction, user = await bot.wait_for(
                    "reaction_add", timeout=30.0, check=check
                )
            except asyncio.TimeoutError:
                await ctx.send("Czas na reakcję minął")
            else:
                guild = ctx.author.guild
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(
                        read_messages=True, send_messages=False
                    ),
                    guild.me: discord.PermissionOverwrite(
                        read_messages=True, send_messages=True
                    ),
                    author: discord.PermissionOverwrite(
                        read_messages=True, send_messages=True
                    ),
                    competitor: discord.PermissionOverwrite(
                        read_messages=True, send_messages=True
                    ),
                }
                channel = await guild.create_text_channel(
                    name="death roll", overwrites=overwrites
                )
                description = "Pierwszy gracz za pomocą komendy .roll 1000 losuje liczbę np. 672. \n następny gracz losuje teraz liczbę z przedziału 672 - .roll 672 \n Gra trwa dopóki któryś z graczy nie wylosuje 1, w ten sposób przegrywając."
                embed = discord.Embed(title="Death Roll", color=0xDD0000)
                embed.add_field(
                    name="Zasady gry w death roll",
                    value=description,
                )
                await channel.send(embed=embed)
                msg = (
                    "Death roll "
                    + author.mention
                    + " vs "
                    + competitor.mention
                    + " rozpoczęty!!🎲 \n Proszę przejść na kanał "
                    + channel.mention
                )
                await ctx.send(msg)
                bot.deathroll_enabled = True
                bot.deathroll_channel = channel
                bot.bot_channel = author.channel
                print(bot.bot_channel)
        else:
            await ctx.send("Debilu siebie oznaczyłeś smh")
    elif bot.deathroll_enabled == True:
        await ctx.send("Death roll w trakcie")
    else:
        await ctx.send("Oznacz istniejącego użytkownika")

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command()
async def catgirl(ctx):
    await ctx.send("tu bedzie AI kocia dziewczynka")

@bot.command()
async def szczur(ctx):
    await ctx.send("<@423941651338100742>")

@bot.command()
async def ruletka(ctx):
    guild = ctx.author.guild
    channel = ctx.author.voice.channel
    members = channel.voice_states
    rand = random.choice(list(members))
    member = guild.get_member(rand)
    mention = "💀💀" + member.mention + "💀💀"
    await ctx.send(mention)
    await member.move_to(None)

# *****VOICE CHANNEL COMMANDS*****
@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    if not isConnected(ctx):
        await channel.connect()
        ctx.voice_client.play(discord.FFmpegPCMAudio(song.join))
    else:
        await ctx.send("Im already connected to a channel")

@bot.command()
async def naura(ctx):
    if isConnected(ctx):
        ctx.voice_client.play(discord.FFmpegPCMAudio(song.leave))
        time.sleep(5)
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("Im not connected to any channel")

# *****MUSIC COMMANDS*****
@bot.command()
async def mortadela(ctx):
    channel = ctx.author.voice.channel
    if not isConnected(ctx):
        await channel.connect()
    ctx.voice_client.play(discord.FFmpegPCMAudio(song.mortadela))
    await ctx.send("Playing Mortadela")

@bot.command()
async def bitwa(ctx):
    channel = ctx.author.voice.channel
    if not isConnected(ctx):
        await channel.connect()
    ctx.voice_client.play(discord.FFmpegPCMAudio(song.bitwa))
    await ctx.send("Playing Bitwa")

@bot.command()
async def gong(ctx):
    channel = ctx.author.voice.channel
    if not isConnected(ctx):
        await channel.connect()
    ctx.voice_client.play(discord.FFmpegPCMAudio(song.gong))
    await ctx.send("GONG")

@bot.command()
async def szczurolap(ctx, member: discord.Member):
    channel = ctx.author.voice.channel
    mention = "😳😳" + member.mention + "😳😳"

    async def zlap(member: discord.Member):
        await member.move_to(None)

    if not isConnected(ctx):
        await channel.connect()
    await ctx.send(mention)
    await ctx.send("Napisz sike zeby sie obronic")
    ctx.voice_client.play(discord.FFmpegPCMAudio(song.szczurolap))

    def check(m):
        return m.content == "sike"

    try:
        msg = await bot.wait_for("message", timeout=5.0, check=check)
    except asyncio.TimeoutError:
        await zlap(member)
    else:
        ctx.voice_client.stop()
        await ctx.send("Uciekłeś sczurołapowi!")

@bot.command()
async def bomba(ctx, bomba: str):
    guild = ctx.author.guild
    channel = ctx.author.voice.channel
    members = channel.voice_states

    async def explosion(ctx):
        await ctx.send("💣💣JEBUUUT💣💣")
        for memberid in members:
            if memberid == 823097409063616542:
                continue
            else:
                member = guild.get_member(memberid)
                await member.move_to(None)
        await ctx.voice_client.disconnect()

    async def defused(ctx):
        ctx.voice_client.stop()
        await ctx.send("Bomb has been defused")
        ctx.voice_client.play(discord.FFmpegPCMAudio(song.bomba_defused))

    def check(m):
        return m.content == "def"

    if bomba == "uwaga":
        if not isConnected(ctx):
            await channel.connect()
        ctx.voice_client.play(discord.FFmpegPCMAudio(song.bomba_uwaga))
        try:
            msg = await bot.wait_for("message", timeout=4.0, check=check)
        except asyncio.TimeoutError:
            await explosion(ctx)
        else:
            await defused(ctx)

    elif bomba == "pierdolnie":
        if not isConnected(ctx):
            await channel.connect()
        ctx.voice_client.play(discord.FFmpegPCMAudio(song.bomba_pierdolnie))
        try:
            msg = await bot.wait_for("message", timeout=1.5, check=check)
        except asyncio.TimeoutError:
            await explosion(ctx)
        else:
            await defused(ctx)

    else:
        await ctx.send("Nieee no tak to nie pierdolnie")

@bot.command()
async def stop(ctx):
    ctx.voice_client.stop()
    await ctx.send("Stopped")

@bot.command()
async def resume(ctx):
    ctx.voice_client.resume()
    await ctx.send("Resumed")

@bot.command()
async def pause(ctx):
    ctx.voice_client.pause()
    await ctx.send("Paused")

# *****BOT RUN COMMAND*****
bot.run(TOKEN)
