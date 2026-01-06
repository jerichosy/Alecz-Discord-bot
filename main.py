import asyncio
import logging
import os
import random
import time

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

        permissions = discord.Permissions.text()
        permissions.update(
            # manage_messages=False,  # comment out for flash cmd ephmeral effect for traditional cmd to work in everyone cmd
            manage_threads=False,  # factory method discord.Permissions.text() override
            manage_webhooks=True,  # other override
        )
        self.INVITE_LINK = discord.utils.oauth_url(
            client_id=self.application_id, permissions=permissions
        )

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print(f"Invite link: {self.INVITE_LINK}")
        print("------")


help_command = commands.MinimalHelpCommand(
    no_category="List of commands", command_attrs={"hidden": True}
)

bot = AleczBot(
    case_insensitive=True,
    command_prefix=commands.when_mentioned_or("a!"),
    activity=discord.Game(name="Looking for people to annoy"),
    intents=discord.Intents.all(),
    owner_id=298454523624554501,  # ! Hardcoded section
    application_id=912346709634457672,  # ! Hardcoded section
    help_command=help_command,
)


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
    count: commands.Range[
        int, 2, 86400
    ],  # Makes sure that at max rate (every sec), it only lasts for a day
    interval: commands.Range[int, 1, None],
    *,
    message,
):
    """Echo a word/sentence/phrase multiple times"""

    await ctx.reply("<:alecz:802600145681645578>", mention_author=False)

    channel = ctx.channel  # This line is necessary
    dm_sendable = True
    for _ in range(count):
        elapsed = time.perf_counter()
        await channel.send(f"{target.mention} {message}")

        # print(mentions)
        if dm_sendable:
            try:
                #                print("trying to send")
                result = await target.send(message)
            #                print(result)
            # bare exception since idk what errors might arise from DM-ing
            except Exception as e:
                dm_sendable = False
                print(f"{dm_sendable=} for {target} | {e}")

        elapsed = time.perf_counter() - elapsed
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
    count: commands.Range[
        int, 2, 1440
    ],  # Makes sure that at max rate (every min), it only lasts for a day
    interval: commands.Range[int, 1, None],
    *,
    easter_egg="",
):
    """Mentions everyone but deletes it shortly afterwards leaving lingering 'phantom' mention notification"""

    if ctx.interaction:
        await ctx.interaction.response.send_message(
            "<:alecz:802600145681645578>", ephemeral=True
        )
    else:
        # Since invokved via traditional cmd, try to delete cmd invoker's message for same ephemeral effect as slash cmd.
        try:
            await ctx.message.delete()
        except:
            print("Could not delete cmd invoker's message in everyone cmd")
            pass

    channel = ctx.channel

    for _ in range(count):
        await channel.send(
            f"@everyone {easter_egg}", delete_after=2
        )  # delete after 2 sec leaving a lingering "phantom" @everyone
        await asyncio.sleep(60 * interval)


@bot.hybrid_command()
async def invite(ctx):
    """Add The Annoying Bot to your server!"""
    await ctx.send(bot.INVITE_LINK)


@bot.command()
async def ping(ctx):
    """Get the bot's current websocket and API latency"""
    start_time = time.perf_counter()
    to_edit = await ctx.send("Testing ping...")
    end_time = time.perf_counter()
    await to_edit.edit(
        content=f"Pong! {round(bot.latency * 1000)}ms | API: {round((end_time - start_time) * 1000)}ms"
    )


@bot.command(aliases=["close", "shutup", "logoff", "stop"])
# Someone who can delete other people's message should be able to shutdown this bot even if it impacts others
# It's okay for now that it impacts others as there's no way to cancel running tasks (cmds)
@has_permissions(manage_messages=True)
async def shutdown(ctx):
    await ctx.send("🛑 Globally shutting down!")
    await bot.close()


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # ! Hardcoded section
    stfu_words = ["talk", "vc"]
    stfu_response = ["Shut the fuck up", "I'm tired"]
    annoyed_response = [
        "What's your problem?",
        "pakyu",
        "PAKYU",
        "Don't bother me, I'm talking with my friends.",
        "maabutan ka sakin",
    ]

    if bot.user.mentioned_in(message) and not message.mention_everyone:
        await message.channel.send(random.choice(annoyed_response))
    elif message.mentions:
        for user in message.mentions:
            if (
                user.id == 766286898632851466  # ! Hardcoded section
            ):  #          766286898632851466 (Alecz' Discord account)
                msg = message.content.lower()
                if any(word in msg for word in stfu_words):
                    await message.channel.send(random.choice(stfu_response))
                break

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
