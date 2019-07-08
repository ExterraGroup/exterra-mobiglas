import sys

import discord
import sentry_sdk
from discord.ext import commands

from mobiglas.bot import MobiGlasBot
from mobiglas.config import settings
from mobiglas.logs import init_loggers

configure_dict = settings.data
logger = init_loggers(settings.logs.path)

print("Loading...")
help_attrs = dict(hidden=True)
MobiGlas = MobiGlasBot(command_prefix=settings.bot.prefix,
                       case_insensitive=True,
                       prefix=settings.bot.prefix,
                       pm_help=True,
                       help_attrs=help_attrs)

modules = ['events', 'fun', 'motion', 'raid', 'rsi', 'rsiadmin', 'background']

for mod in modules:
    try:
        MobiGlas.load_extension(f"mobiglas.modules.{mod}")
    except Exception as e:
        print(f'**Error when loading extension {mod}:**\n{type(e).__name__}: {e}')
    else:
        if 'debug' in sys.argv[1:]:
            print(f'Loaded {mod} extension.')

if settings.sentry_dsn.enabled:
    sentry_sdk.init(settings.sentry_dsn.url)


@MobiGlas.event
async def on_ready():
    MobiGlas.owner = discord.utils.get(MobiGlas.get_all_members(), id=settings.bot.owners[0])
    await _print(MobiGlas.owner, 'Starting up...')
    server_count = len(MobiGlas.guilds)
    member_count = 0
    for guild in MobiGlas.guilds:
        member_count += guild.member_count
    await _print(MobiGlas.owner, f"MobiGlas > {server_count} servers connected.\n{member_count} members found.")
    # todo: await maint_start()


@MobiGlas.event
async def on_member_join(member):
    """Welcome message to the server and some basic instructions."""
    guild = member.guild
    welcome_dict = settings.data.welcome

    if not welcome_dict.enabled:
        return

    # Construct Welcome Message
    welcome_message = eval(welcome_dict.msg)

    if welcome_dict.channel == 'dm':
        send_to = member
    elif str(welcome_dict.channel).isdigit():
        send_to = discord.utils.get(guild.text_channels,
                                    id=int(welcome_dict.channel))
    else:
        send_to = discord.utils.get(guild.text_channels,
                                    name=welcome_dict.channel)

    if send_to:
        if welcome_message.startswith("[") and welcome_message.endswith("]"):
            await send_to.send(embed=discord.Embed(colour=guild.me.colour,
                                                   description=welcome_message[1:-1]))
        else:
            await send_to.send(welcome_message.format(server=guild.name, user=member.mention))
    else:
        return


@MobiGlas.command()
@commands.has_permissions(manage_guild=True)
async def welcome(ctx, user: discord.Member = None):
    """Test welcome on yourself or mentioned member.

    Usage: !welcome [@member]"""
    if (not user):
        user = ctx.author
    await on_member_join(user)


async def _print(owner, message):
    if 'launcher' in sys.argv[1:]:
        if 'debug' not in sys.argv[1:]:
            await owner.send(message)
    print(message)
    logger.info(message)


MobiGlas.run(settings.bot.token)
