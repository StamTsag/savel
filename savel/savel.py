import discord
from discord.ext import commands
from dotenv import load_dotenv
from os import environ

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

savel = commands.Bot(intents=intents, command_prefix=".")


async def get_embed(ctx: discord.Message, title="") -> discord.Embed:
    embed = discord.Embed(title=title, color=discord.Color.from_str("#ffffff"))

    embed.set_footer(text=f"Sent for {ctx.author.name} in #{ctx.channel.name}")

    return embed


@savel.event
async def on_ready():
    print("Savel UP.")

    game = discord.Game(".help | /help")

    await savel.change_presence(activity=game, status=discord.Status.online)


@savel.event
async def on_message(message: discord.Message):
    if message.author == savel.user:
        return

    print(message.author)

    if message.author.name != "shadofer":
        return

    await savel.process_commands(message)


@savel.remove_command("help")
@savel.command(description="This!")
async def help(ctx: discord.Message):
    embed = await get_embed(ctx, "Savel Commands")

    all_commands = savel.commands

    for cmd in all_commands:
        embed.add_field(name=f"`{cmd}`: {cmd.description}", value="")

    await ctx.channel.send(embed=embed)


@savel.command(description="The code behind this bot")
async def code(ctx: discord.Message):
    embed = await get_embed(ctx, "Savel Code")

    embed.add_field(
        name="Savel is open-sourced at https://github.com/Shadofer/savel", value="\n"
    )

    await ctx.channel.send(embed=embed)


savel.run(environ.get("SAVEL_TOKEN"))
