import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from dotenv import load_dotenv
import os
import asyncio
import random
import time
from datetime import datetime

import logging

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

help_command = commands.MinimalHelpCommand(
    no_category="List of commands", command_attrs={"hidden": True}
)

bot = commands.Bot(
    case_insensitive=True,
    command_prefix=commands.when_mentioned_or("a!"),
    activity=discord.Game(name="Looking for people to annoy"),
    help_command=help_command,
)  # , description=description

stfu_words = ["talk", "vc"]

stfu_response = ["Shut the fuck up", "I'm tired"]

annoyed_response = [
    "What's your problem?",
    "pakyu",
    "PAKYU",
    "Don't bother me, I'm talking with my friends.",
]


@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


@bot.command()
#@commands.is_owner()
async def annoy(ctx, id: int, count: int, interval: int, *, msg):
    for i in range(count):
        user_id = str(id)
        user = await bot.fetch_user(id)
        await ctx.send(f"<@{user_id}> {msg}")
        await user.send(f"{msg}")
        await asyncio.sleep(interval)


@bot.command(hidden=True)
@commands.is_owner()
async def stillalive(ctx):
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        await ctx.send(f"{current_time} still alive")
        await asyncio.sleep(600)


@bot.command()
async def ping(ctx):
    """Get the bot's current websocket and API latency"""
    start_time = time.time()
    to_edit = await ctx.send("Testing ping...")
    end_time = time.time()
    await to_edit.edit(
        content=f"Pong! {round(bot.latency * 1000)}ms | API: {round((end_time - start_time) * 1000)}ms"
    )


@bot.command(aliases=["code", "showcode", "sc"])
async def sourcecode(ctx):
    """Have the bot upload it's own sourcecode here in Discord"""
    await ctx.send(file=discord.File("alecz.py"))


@bot.command(aliases=["close", "shutup", "logoff", "stop"])
@has_permissions(administrator=True)
async def shutdown(ctx):
    await ctx.send("🛑 Shutting down!")
    await bot.close()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    msg = message.content.lower()

    if bot.user.mentioned_in(message):
        await message.channel.send(random.choice(annoyed_response))
    elif message.mentions:
        for user in message.mentions:
            if user.id == 766286898632851466:  # 766286898632851466
                if any(word in msg for word in stfu_words):
                    await message.channel.send(random.choice(stfu_response))
                else:
                    # await message.channel.send(f"{msg} daw")
                    pass
                    # Doing it through DM as well might be too spammy
                    # await user.send('{msg}')

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        pass
    else:
        await ctx.send(error)


bot.load_extension("jishaku")

load_dotenv()
bot.run(os.getenv("ALECZ_TOKEN"))
