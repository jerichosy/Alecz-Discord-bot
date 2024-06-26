import asyncio
import logging
import os
import random
import time
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.ext.commands.cooldowns import BucketType
from dotenv import load_dotenv

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

load_dotenv()


class AleczBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.INVITE_LINK = discord.utils.oauth_url(
            client_id=self.application_id, permissions=discord.Permissions.advanced()
        )

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")


help_command = commands.MinimalHelpCommand(
    no_category="List of commands", command_attrs={"hidden": True}
)

bot = AleczBot(
    case_insensitive=True,
    command_prefix=commands.when_mentioned_or("a!"),
    activity=discord.Game(name="Looking for people to annoy"),
    intents=discord.Intents.all(),
    owner_id=298454523624554501,
    application_id=912346709634457672,
    help_command=help_command,
)


# TODO: Optimize mentions (if still being developed) to avoid unnecessarily hitting rate limits
@bot.hybrid_command()
@app_commands.describe(count="No. of times to repeat the annoying message.")
@app_commands.describe(
    interval="Interval in seconds between the repeating annoying messages."
)
@app_commands.describe(
    target="User that will be mentioned at the start of every annoying message. The user will also be DM'ed."
)
@app_commands.describe(message="The word/sentence/phrase to repeat.")
async def annoy(
    ctx,
    target: discord.User,
    count: commands.Range[int, 2, 86400],
    interval: commands.Range[int, 1, None],
    *,
    message,
):
    """Echo a word/sentence/phrase multiple times"""

    #    mentions = [mention for mention in ctx.message.mentions]
    #    if not mentions:
    #        matches = re.findall(r"<@!?([0-9]{15,20})>", ctx.message)
    #        mentions = [ctx.guild.get_member(int(match)) for match in matches]
    #    print(message, mentions)  # debug

    await ctx.reply("<:alecz:802600145681645578>")

    channel = ctx.channel  # This line is necessary
    sendable = True
    for _ in range(count):
        elapsed = time.time()
        await channel.send(f"{target.mention} {message}")

        # print(mentions)
        if sendable:
            try:
                #                print("trying to send")
                result = await target.send(message)
            #                print(result)
            except (discord.HTTPException, AttributeError):
                sendable = False

        elapsed = time.time() - elapsed
        new_interval = interval - elapsed
        # print(new_interval)

        if new_interval > 0:
            await asyncio.sleep(new_interval)


# This is so dumb and annoying (thanks to Daniel and Jehu)
@bot.hybrid_command()
@app_commands.describe(count="No. of times to annoy @everyone.")
@app_commands.describe(interval="Interval in minutes between the mentions.")
@app_commands.describe(
    easter_egg="Message that will be appended after the @everyone mention."
)
async def everyone(
    ctx,
    count: commands.Range[int, 2, 1440],
    interval: commands.Range[int, 1, None],
    *,
    easter_egg=None,
):
    """Mentions everyone but deletes it shortly afterwards leaving lingering 'phantom' mention notification"""

    if ctx.interaction:
        await ctx.interaction.response.send_message(
            "<:alecz:802600145681645578>", ephemeral=True
        )
    else:
        await ctx.message.delete()

    channel = ctx.channel

    for _ in range(count):
        await channel.send(
            f"@everyone {easter_egg if easter_egg else ''}", delete_after=2
        )  # delete after 2 sec leaving a lingering "phantom" @everyone
        await asyncio.sleep(60 * interval)


@bot.hybrid_command()
async def invite(ctx):
    """Add The Annoying Bot to your server!"""
    await ctx.send(bot.INVITE_LINK)


@bot.command()
async def ping(ctx):
    """Get the bot's current websocket and API latency"""
    start_time = time.time()
    to_edit = await ctx.send("Testing ping...")
    end_time = time.time()
    await to_edit.edit(
        content=f"Pong! {round(bot.latency * 1000)}ms | API: {round((end_time - start_time) * 1000)}ms"
    )


@bot.command(aliases=["close", "shutup", "logoff", "stop"])
@has_permissions(administrator=True)
async def shutdown(ctx):
    await ctx.send("🛑 Shutting down!")
    await bot.close()


@bot.command(hidden=True)
@commands.is_owner()
@commands.max_concurrency(1, per=BucketType.default, wait=False)
async def stillalive(ctx):
    interval_in_seconds = 60 * 10  # 10 mins

    for _ in range(86400 // interval_in_seconds):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        await ctx.send(f"{current_time} still alive")
        await asyncio.sleep(interval_in_seconds)


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    stfu_words = ["talk", "vc"]

    stfu_response = ["Shut the fuck up", "I'm tired"]

    annoyed_response = [
        "What's your problem?",
        "pakyu",
        "PAKYU",
        "Don't bother me, I'm talking with my friends.",
        "maabutan ka sakin",
    ]

    if bot.user.mentioned_in(message):
        await message.channel.send(random.choice(annoyed_response))
    elif message.mentions:
        for user in message.mentions:
            if (
                user.id == 766286898632851466
            ):  # 766286898632851466 (Alecz' Discord account)
                msg = message.content.lower()
                if any(word in msg for word in stfu_words):
                    await message.channel.send(random.choice(stfu_response))
                # else:
                #     await message.channel.send(f"{msg} daw")
                #     await user.send('{msg}')  # Doing it through DM as well might be too spammy

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        pass
    else:
        await ctx.send(error)


async def main():
    await bot.load_extension("jishaku")

    await bot.start(os.getenv("ALECZ_TOKEN"))


asyncio.run(main())
