import discord
from discord.ext import commands
from dotenv import load_dotenv
from os import environ, path
from json import load, dump
from time import time


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# This equals to bool yes
use_volume = environ.get("SAVEL_USE_VOLUME", "False") == "True"

owner = environ.get("SAVEL_OWNER")

start = time()

savel = commands.Bot(intents=intents, command_prefix=".")


leveling_file = f'{"/savel-data/" if use_volume == True else ""}savel-levels.json'
config_file = f'{"/savel-data/" if use_volume == True else ""}savel-conf.json'


def setup_files():
    if not path.isfile(leveling_file):
        with open(leveling_file, "w") as f:
            f.write("{}")

    if not path.isfile(config_file):
        with open(config_file, "w") as f:
            f.write("{}")


def check_entry(id: str):
    with open(leveling_file, "r") as f:
        content = load(f)

        if not (id in content):
            content[id] = {"xp": 0, "level": 1}

            with open(leveling_file, "w") as f:
                dump(content, f)


async def add_xp(id: str, ctx: discord.Message):
    check_entry(id)

    with open(leveling_file, "r") as f:
        content = load(f)

        # Entry already exists
        content[id] = {"xp": content[id]["xp"] + 10, "level": content[id]["level"]}

        with open(leveling_file, "w") as f:
            dump(content, f)

        await check_level(id, ctx)


def get_xp(id: str):
    check_entry(id)

    with open(leveling_file, "r") as f:
        content = load(f)

        return content[id]["xp"]


def get_target_xp(id: str):
    check_entry(id)

    with open(leveling_file, "r") as f:
        content = load(f)

        return (content[id]["level"] + 1) * 100


def get_total_xp(id: str):
    check_entry(id)

    with open(leveling_file, "r") as f:
        content = load(f)

        total_xp = 0

        for i in range(1, content[id]["level"] + 1):
            # No xp in level 1
            if i == 1:
                continue

            total_xp += i * 100

        total_xp += content[id]["xp"]

        return total_xp


def get_level(id: str):
    check_entry(id)

    with open(leveling_file, "r") as f:
        content = load(f)

        return content[id]["level"]


async def check_level(id: str, message: discord.Message):
    check_entry(id)

    with open(leveling_file, "r") as f:
        content = load(f)

        xp = content[id]["xp"]
        level = content[id]["level"]

        target_xp = (level + 1) * 100

        if xp >= target_xp:
            xp = 0
            level += 1

            content[id] = {"xp": xp, "level": level}

            with open(leveling_file, "w") as f:
                dump(content, f)

            await message.channel.send(
                content=f"{message.author.mention} is now level {level}!"
            )


async def get_embed(ctx: discord.Message, title="") -> discord.Embed:
    embed = discord.Embed(
        title=title,
        color=discord.Color.from_str("#ffffff"),
    )

    embed.set_footer(text=f"Sent for {ctx.author.name} in #{ctx.channel.name}")

    return embed


@savel.event
async def on_ready():
    setup_files()

    print("Savel UP.")

    game = discord.Game(".help | /help")

    await savel.change_presence(activity=game, status=discord.Status.online)


@savel.event
async def on_message(message: discord.Message):
    if message.author == savel.user or message.author.bot:
        return

    # Commands dont give xp
    if message.content.startswith("."):
        for command in savel.all_commands:
            if message.content.find(command) != -1:
                await savel.process_commands(message)
                return

        if not environ.get("SAVEL_DEV") == True:
            await add_xp(str(message.author.id), message)

    else:
        if not environ.get("SAVEL_DEV") == True:
            await add_xp(str(message.author.id), message)


@savel.remove_command("help")
@savel.hybrid_command(description="This!")
async def help(ctx: discord.Message):
    embed = await get_embed(ctx, "Savel Commands")

    for cmd in savel.commands:
        if cmd.description != "owner-only":
            embed.add_field(name=f"`{cmd}`: {cmd.description}", value="")

    await ctx.channel.send(embed=embed)


@savel.hybrid_command(description="The code behind this bot")
async def code(ctx: discord.Message):
    embed = await get_embed(ctx, "Savel Code")

    embed.add_field(
        name="Savel is open-sourced at https://github.com/Shadofer/savel", value=""
    )

    await ctx.channel.send(embed=embed)


@savel.hybrid_command(description="Shows your level stats")
async def level(ctx: discord.Message, mention: discord.User = None):
    if mention:
        if mention.bot:
            return

    embed = await get_embed(
        ctx, title=f"{ctx.author.name if not mention else mention.name}'s level"
    )

    target_id = str(ctx.author.id) if not mention else str(mention.id)

    embed.add_field(
        name=f"Level: {get_level(target_id)}, XP: {get_xp(target_id)}/{get_target_xp(target_id)}",
        value="",
    )

    await ctx.channel.send(embed=embed)


@savel.hybrid_command(description="Shows the server leaderboard")
async def top(ctx: discord.Message, count: int = 10):
    embed = await get_embed(ctx, title=f"{ctx.guild.name}'s leaderboard")

    total_members = []
    total_xp = []
    selected_members = []
    selected_xp = []

    with open(leveling_file, "r") as f:
        content = load(f)

        async for member in ctx.guild.fetch_members():
            if str(member.id) in content:
                total_members.append(member)
                total_xp.append(get_total_xp(str(member.id)))

    total_xp.sort()
    total_xp = total_xp[::-1]

    selected_xp = total_xp[:count]

    for xp in selected_xp:
        for member in total_members:
            if get_total_xp(str(member.id)) == xp:
                selected_members.append(member)

    for member in selected_members:
        embed.add_field(
            name=member.name,
            value=f"Level: {get_level(str(member.id))}",
        )

    await ctx.channel.send(embed=embed)


@savel.hybrid_command(description="Measures bot latency")
async def ping(ctx: discord.Message):
    embed = await get_embed(ctx)

    embed.add_field(name="Latency", value=f"{round(savel.latency, 2)}ms")

    await ctx.channel.send(embed=embed)


@savel.hybrid_command(description="Displays bot uptime")
async def uptime(ctx: discord.Message):
    ms = int(time()) - int(start)

    seconds = (ms) % 60
    seconds = int(seconds)

    minutes = (ms / (60)) % 60
    minutes = int(minutes)

    hours = (ms / (60 * 60)) % 24

    embed = await get_embed(ctx)

    embed.add_field(
        name="Uptime",
        value=f"{str(hours) + ' hours ' if hours >= 1 else ''}{str(minutes) + ' minutes ' if minutes >= 1 else ''}{str(seconds) + ' seconds ' if seconds >= 1 else ''}",
    )

    await ctx.channel.send(embed=embed)


@savel.hybrid_command(description="owner-only")
async def fsnames(ctx: discord.Message):
    # Must have owner and be equal to it
    if not owner:
        return

    if ctx.author.name != owner:
        return

    embed = await get_embed(ctx)

    embed.add_field(name="Leveling file", value=leveling_file)
    embed.add_field(name="Configuration file", value=config_file)

    await ctx.channel.send(embed=embed)


@savel.hybrid_command(description="owner-only")
async def restart(ctx: discord.Message):
    # Must have owner and be equal to it
    if not owner:
        return

    if ctx.author.name != owner:
        return

    embed = await get_embed(ctx)

    embed.add_field(name="Savel restarting...", value="")

    await ctx.channel.send(embed=embed)

    exit(1)


savel.run(environ.get("SAVEL_TOKEN"))
