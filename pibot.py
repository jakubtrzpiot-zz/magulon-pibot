import discord
import ffmpeg
import time
import random
import asyncio
import numpy as np
from discord.ext import commands


# *****STATICS*****
TOKEN = "ODIzMDk3NDA5MDYzNjE2NTQy.YFb3Mg.Q44ppuB-4KhMCAL2VZAp81LIZ2s"
description = "Gowno z cebula"


class song:
    mortadela = "/home/pi/pibot/assets/mortadela.mp3"
    bitwa = "/home/pi/pibot/assets/bitwa.mp3"
    gong = "/home/pi/pibot/assets/gong.mp3"
    join = "/home/pi/pibot/assets/onii-chan.mp3"
    leave = "/home/pi/pibot/assets/oyasumi.mp3"
    szczurolap = "/home/pi/pibot/assets/szczurolap.mp3"
    bomba_pierdolnie = "/home/pi/pibot/assets/bomba_pierdolnie.mp3"
    bomba_uwaga = "/home/pi/pibot/assets/bomba_uwaga.mp3"
    bomba_defused = "/home/pi/pibot/assets/bomba_defused.mp3"


# *****INTENTS*****
intents = discord.Intents.default()
intents.members = True


def isConnected(ctx):
    return ctx.voice_client


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
bot.bot_channel_id = 779297299188154369


@bot.event
async def on_member_join(member):
    msg = "Siema " + mention + "! Wpisz help zeby sprawdzic liste komend"
    await ctx.send(msg)


async def on_deathroll(rand: int, looser: discord.User):
    if rand == 1:
        msg = "🔫" + looser.mention + " przegrywa death roll!🔫"
        channel = bot.get_channel(779297299188154369)
        await channel.send(msg)
        bot.deathroll_enabled = False
        return_link = "Wróć na kanał " + channel.mention
        await bot.deathroll_channel.send(return_link)
        time.sleep(5)
        await bot.deathroll_channel.delete()
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
async def users(ctx, guildid: int = 538652988621979649):
    server = bot.get_guild(guildid)
    title = "Id członków serwera " + server.name
    embed = discord.Embed(title=title)
    for member in bot.get_all_members():
        if member.guild.id == guildid:
            msg = member.display_name + " - " + str(member.id)
            embed.add_field(name=member.display_name, value=member.id)
    await ctx.send(embed=embed)


@bot.command()
async def usun(ctx, msgid: int = None):
    msg = await ctx.channel.fetch_message(msgid)
    if msgid == None:
        await ctx.send("Wpisz poprawne id wiadomosci")
    await msg.delete()


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
    users = channel.voice_states
    rand = random.choice(list(users))
    user = guild.get_member(rand)
    mention = "💀💀" + user.mention + "💀💀"
    await ctx.send(mention)
    await user.move_to(None)


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
async def szczurolap(ctx, user: discord.User):
    channel = ctx.author.voice.channel
    mention = "😳😳" + user.mention + "😳😳"

    async def zlap(user: discord.User):
        await user.move_to(None)

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
        await zlap(user)
    else:
        ctx.voice_client.stop()
        await ctx.send("Uciekłeś sczurołapowi!")


@bot.command()
async def bomba(ctx, bomba: str):
    guild = ctx.author.guild
    channel = ctx.author.voice.channel
    users = channel.voice_states

    async def explosion(ctx):
        await ctx.send("💣💣JEBUUUT💣💣")
        for userid in users:
            if userid == 823097409063616542:
                continue
            else:
                user = guild.get_member(userid)
                await user.move_to(None)
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
