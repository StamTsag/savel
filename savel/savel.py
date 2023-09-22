import discord
from discord.ext import commands
from dotenv import load_dotenv
from os import environ, path
from json import load, dump
from time import time
from random import randrange

# Should change manually if updates have been commited
VERSION = "1.0.0"

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


def check_server_entry(server: str):
    with open(config_file, "r") as f:
        content = load(f)

        if not (server in content):
            content[server] = {
                "channel": "-1",
                "welcome": "-1",
                "goodbye": "-1",
                "shadows": "[]",
                "autorole": "-1",
                "counting": "-1",
            }

            with open(config_file, "w") as f:
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

            if get_channel(message.guild.id) != -1:
                await savel.get_channel(get_channel(message.guild.id)).send(
                    content=f"{message.author.mention} is now level {level}!",
                )

            else:
                await message.channel.send(
                    content=f"{message.author.mention} is now level {level}!",
                )

    check_entry(id)

    with open(leveling_file, "r") as f:
        content = load(f)

        return content[id]["level"]


def get_channel(server: str):
    server = str(server)

    check_server_entry(server)

    with open(config_file, "r") as f:
        content = load(f)

        return int(content[server]["channel"])


def set_channel(server: str, channel: str):
    server = str(server)

    check_server_entry(server)

    with open(config_file, "r") as f:
        content = load(f)

        content[server]["channel"] = str(channel)

        with open(config_file, "w") as f:
            dump(content, f)


def get_welcome(server: str):
    server = str(server)

    check_server_entry(server)

    with open(config_file, "r") as f:
        content = load(f)

        return int(content[server]["welcome"])


def set_welcome(server: str, channel: str):
    server = str(server)

    check_server_entry(server)

    with open(config_file, "r") as f:
        content = load(f)

        content[server]["welcome"] = str(channel)

        with open(config_file, "w") as f:
            dump(content, f)


def get_goodbye(server: str):
    server = str(server)

    check_server_entry(server)

    with open(config_file, "r") as f:
        content = load(f)

        return int(content[server]["goodbye"])


def set_goodbye(server: str, channel: str):
    server = str(server)

    check_server_entry(server)

    with open(config_file, "r") as f:
        content = load(f)

        content[server]["goodbye"] = str(channel)

        with open(config_file, "w") as f:
            dump(content, f)


def get_autorole(server: str):
    server = str(server)

    check_server_entry(server)

    with open(config_file, "r") as f:
        content = load(f)

        return int(content[server]["autorole"])


def set_autorole(server: str, role: str):
    server = str(server)

    check_server_entry(server)

    with open(config_file, "r") as f:
        content = load(f)

        content[server]["autorole"] = str(role)

        with open(config_file, "w") as f:
            dump(content, f)


def get_counting(server: str):
    server = str(server)

    check_server_entry(server)

    with open(config_file, "r") as f:
        content = load(f)

        if "counting" in content[server]:
            return int(content[server]["counting"])

        else:
            return -1


def set_counting(server: str, channel: str):
    server = str(server)

    check_server_entry(server)

    with open(config_file, "r") as f:
        content = load(f)

        content[server]["counting"] = str(channel)

        with open(config_file, "w") as f:
            dump(content, f)


def get_shadows(server: str):
    server = str(server)

    check_server_entry(server)

    with open(config_file, "r") as f:
        content = load(f)

        if "shadows" in content[server]:
            return content[server]["shadows"]

        else:
            return []


def add_shadow(server: str, id: str):
    server = str(server)
    id = str(id)

    check_server_entry(server)

    with open(config_file, "r") as f:
        content = load(f)

        shadows = []
        removed = False

        if "shadows" in content[server]:
            shadows = list(content[server]["shadows"])

        if not (id in shadows):
            shadows.append(id)

            removed = False

        else:
            shadows.remove(id)

            removed = True

        content[server]["shadows"] = shadows

        # Update shadows key anyway, init
        with open(config_file, "w") as f:
            dump(content, f)

            return removed


async def get_embed(ctx: discord.Message, title="", hide_footer=False) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        color=discord.Color.from_str("#ffffff"),
    )

    if not hide_footer:
        embed.set_footer(text=f"Sent for {ctx.author.name} in #{ctx.channel.name}")

    return embed


async def send_error_embed(ctx: discord.Message, msg: str) -> discord.Embed:
    embed = discord.Embed(
        title="",
        color=discord.Color.from_str("#ffffff"),
    )

    embed.add_field(name="Savel command error", value=msg)

    embed.set_footer(text=f"Sent for {ctx.author.name} in #{ctx.channel.name}")

    await ctx.channel.send(embed=embed)


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

    # Commands / Counting dont give xp
    if message.channel.id == get_counting(message.guild.id):
        if not message.content.isnumeric():
            await message.delete()

            return

        messages = [message async for message in message.channel.history(limit=2)]
        target_msg = messages[-1]

        if int(message.content) != int(target_msg.content) + 1:
            await message.delete()

        else:
            await message.add_reaction("✅")

        return

    elif message.content.startswith("."):
        for command in savel.all_commands:
            if message.content.find(command) != -1:
                await savel.process_commands(message)
                return

        if not environ.get("SAVEL_DEV") == True:
            await add_xp(str(message.author.id), message)

    else:
        if not environ.get("SAVEL_DEV") == True:
            await add_xp(str(message.author.id), message)


@savel.event
async def on_member_join(member: discord.Member):
    target = get_welcome(member.guild.id)

    if target != -1:
        await savel.get_channel(target).send(f"{member.mention} has joined!")

    if str(member.id) in get_shadows(member.guild.id):
        await member.ban(reason="User in Savel shadow-bans list")

    else:
        if get_autorole(member.guild.id) != -1:
            await member.add_roles(member.guild.get_role(get_autorole(member.guild.id)))


@savel.event
async def on_member_remove(member: discord.Member):
    target = get_goodbye(member.guild.id)

    if target != -1:
        await savel.get_channel(target).send(f"{member.mention} has left!")


@savel.remove_command("help")
@savel.hybrid_command(description="This!")
async def help(ctx: discord.Message):
    embed = await get_embed(ctx, "Savel Commands")

    for cmd in savel.commands:
        if cmd.description != "owner-only" and cmd.description != "hidden":
            embed.add_field(name=f"`{cmd}`: {cmd.description}", value="", inline=False)

    await ctx.channel.send(embed=embed)


@savel.hybrid_command(description="Owner commands")
async def helpowner(ctx: discord.Message):
    if not owner:
        return

    if ctx.author.name != owner:
        return

    embed = await get_embed(ctx, "Savel Owner Commands")

    for cmd in savel.commands:
        if cmd.description == "owner-only":
            embed.add_field(name=f"`{cmd}`", value="", inline=False)

    await ctx.channel.send(embed=embed)


@savel.hybrid_command(description="Shows the invite link")
async def invite(ctx: discord.Message):
    embed = await get_embed(ctx)

    embed.add_field(
        name="Invite Savel using the link below",
        value="https://discord.com/api/oauth2/authorize?client_id=1148648338137301002&permissions=10256&scope=bot",
    )

    await ctx.channel.send(embed=embed)


@savel.hybrid_command(description="The code behind this bot")
async def code(ctx: discord.Message):
    embed = await get_embed(ctx, "Savel Code")

    embed.add_field(
        name="Savel is open-sourced at https://github.com/Shadofer/savel", value=""
    )

    await ctx.channel.send(embed=embed)


@savel.hybrid_command(name="8ball", description="Try your luck")
async def _8ball(ctx: discord.Message, q: str):
    if not q:
        await send_error_embed(ctx, "Ask me something bruh")
        return

    choices = [
        "Not likely",
        "I don't care",
        "No",
        "Yes",
        "Hopefully not",
        "Dont ask me",
        "Most likely",
        "Improbable",
        "Impossible",
        "Hell nah",
        "Hard to say",
        "Seen",
        "Waste of time",
        "Thy is the truth",
        "Thy is false",
        "Chances are: no",
        "Chances are: yes",
        "Ask me later",
        "I'm gonna pretend you didnt just ask that",
        "Who",
        "Sus",
        "I'm blind",
        "No snitching",
        "I am just a bot dummy",
        "Of course",
        "Ain't no way",
        "100%",
        "0%",
        "50%",
        "I'm dumb",
        "Later",
        "Delivered",
    ]

    choice = choices[randrange(0, len(choices) + 1)]

    embed = await get_embed(ctx, choice, True)

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
    selected_usernames = []
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

    for i, member in enumerate(selected_members):
        if member.name not in selected_usernames:
            selected_usernames.append(member.name)

            embed.add_field(
                name=f"{i + 1}. {member.name}",
                value=f"Level: {get_level(str(member.id))}",
                inline=False,
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

    hours = int((ms / (60 * 60)) % 24)

    embed = await get_embed(ctx)

    embed.add_field(
        name="Uptime",
        value=f"{str(hours) + ' hours ' if hours >= 1 else ''}{str(minutes) + ' minutes ' if minutes >= 1 else ''}{str(seconds) + ' seconds ' if seconds >= 1 else ''}",
    )

    await ctx.channel.send(embed=embed)


@savel.hybrid_command(description="hidden")
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


@savel.hybrid_command(description="Shows bot version")
async def version(ctx: discord.Message):
    embed = await get_embed(ctx)

    embed.add_field(name="Savel version", value=VERSION)

    await ctx.channel.send(embed=embed)


@savel.hybrid_command(description="hidden")
async def restart(ctx: discord.Message):
    # Must have owner and be equal to it
    if not owner:
        return

    if ctx.author.name != owner:
        return

    await ctx.channel.send(embed=await get_embed(ctx, "Savel restarting...", True))

    exit(1)


@savel.hybrid_command(description="hidden")
async def shutdown(ctx: discord.Message):
    # Must have owner and be equal to it
    if not owner:
        return

    if ctx.author.name != owner:
        return

    await ctx.channel.send(embed=await get_embed(ctx, "Savel shutting down...", True))

    exit(0)


@savel.hybrid_command(description="owner-only")
async def channel(ctx: discord.Message, channel_arg: discord.TextChannel):
    # Must have owner and be equal to it
    if not owner:
        return

    if ctx.author.name != owner and not ctx.author.guild_permissions.administrator:
        return

    set_channel(ctx.guild.id, channel_arg.id)

    await ctx.channel.send(
        embed=await get_embed(
            ctx, f"Savel leveling logs set to {channel_arg.name}", True
        )
    )


@savel.hybrid_command(description="owner-only")
async def welcome(ctx: discord.Message, channel_arg: discord.TextChannel):
    # Must have owner and be equal to it
    if not owner:
        return

    if ctx.author.name != owner and not ctx.author.guild_permissions.administrator:
        return

    set_welcome(ctx.guild.id, channel_arg.id)

    await ctx.channel.send(
        embed=await get_embed(
            ctx, f"Savel welcoming logs set to {channel_arg.name}", True
        )
    )


@savel.hybrid_command(description="owner-only")
async def goodbye(ctx: discord.Message, channel_arg: discord.TextChannel):
    # Must have owner and be equal to it
    if not owner:
        return

    if ctx.author.name != owner and not ctx.author.guild_permissions.administrator:
        return

    set_goodbye(ctx.guild.id, channel_arg.id)

    await ctx.channel.send(
        embed=await get_embed(
            ctx, f"Savel goodbye logs set to {channel_arg.name}", True
        )
    )


@savel.hybrid_command(description="owner-only")
async def counting(ctx: discord.Message, channel_arg: discord.TextChannel):
    # Must have owner and be equal to it
    if not owner:
        return

    if ctx.author.name != owner and not ctx.author.guild_permissions.administrator:
        return

    set_counting(ctx.guild.id, channel_arg.id)

    await savel.get_channel(channel_arg.id).send("0")

    await ctx.channel.send(
        embed=await get_embed(ctx, f"Savel counting set to {channel_arg.name}", True)
    )


@savel.hybrid_command(description="owner-only")
async def autorole(ctx: discord.Message, role_arg: discord.Role = None):
    # Must have owner and be equal to it
    if not owner:
        return

    if ctx.author.name != owner and not ctx.author.guild_permissions.administrator:
        return

    if role_arg:
        set_autorole(ctx.guild.id, role_arg.id)

        await ctx.channel.send(
            embed=await get_embed(
                ctx, f"Savel target autorole set to {role_arg.name}", True
            )
        )

    else:
        set_autorole(ctx.guild.id, -1)

        await ctx.channel.send(
            embed=await get_embed(ctx, f"Savel autorole disabled", True)
        )


@savel.hybrid_command(description="owner-only")
async def shadowban(ctx: discord.Message, id: str):
    # Must have owner and be equal to it
    if not owner:
        return

    if ctx.author.name != owner and not ctx.author.guild_permissions.administrator:
        return

    removed = add_shadow(ctx.guild.id, id)

    await ctx.channel.send(
        embed=await get_embed(
            ctx, f"{'Removed s' if removed else 'S'}hadow-banned user {id}", True
        )
    )


savel.run(environ.get("SAVEL_TOKEN"))
