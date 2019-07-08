import asyncio
import re
import textwrap

import discord

from mobiglas import emoji


async def print_logs(ctx, logs):
    if len(logs) != 0:
        await ctx.send('\n'.join(logs))
    else:
        await ctx.send('No updates.')
    return


def find_guild_username(ctx, name):
    """Searches the guild for the username or handle and returns a discord Member object
    :param ctx: Session Context
    :param name: name of user {discord username or handle}
    :return: discord.Member
    """
    # try account nickname next
    discord_member = discord.utils.get(ctx.guild.members, nick=name)
    if discord_member is not None:
        return discord_member

    # try account name first
    discord_member = discord.utils.get(ctx.guild.members, name=name)
    if discord_member is not None:
        return discord_member

    return None


def get_member_nickname(member):
    return member.name if not member.nick else member.nick


async def add_guild_role(ctx, guild_member, role_names, reason=None):
    """Add role(s) to a member
    :param ctx: Session Context
    :param guild_member: discord.Member
    :param role_names: String[] of role names
    :param reason: (optional) a reason for adding the role
    """
    roles = get_role_datum(ctx, role_names)
    await guild_member.add_roles(*roles, reason=reason)
    return


async def remove_guild_role(ctx, guild_member, role_names, reason=None):
    """Remove role(s) from a member
    :param ctx: Session Context
    :param guild_member: discord.Member
    :param role_names: String[] of role names
    :param reason: (optional) a reason for adding the role
    """
    roles = get_role_datum(ctx, role_names)
    await guild_member.remove_roles(*roles, reason=reason)
    return


def get_role_datum(ctx, role_names):
    """Converts String[] of role names to discord.Member[] of roles
    :param ctx: Session Context
    :param role_names: String[] of role names
    :return: discord.Member[]
    """
    roles = []
    for role_name in santinize_roles(role_names):
        roles.append(discord.utils.get(ctx.guild.roles, name=role_name))
    return roles


def santinize_roles(role_names):
    """Removes reserved role names from a list of role names
    :param role_names: String[] of role names
    :return: String[] of role names
    """
    from .config import settings
    reserved_roles = settings.bot.reserved.roles
    tmp = role_names.copy()
    for name in role_names:
        if name in reserved_roles:
            tmp.remove(name)

    return tmp


def santinize_users(users):
    """Removes bot user from a list of user names

    :param users: String[] of user names
    :return: String[] of user names
    """
    from .config import settings
    bot_name = settings.bot.name
    users.remove(bot_name)

    return users


def wrap_line(line: str, width=29):
    """Wraps a long string into multiple lines with a default width of 29
    :param width: maximum length of 1 row
    :param line: str
    :return: str
    """
    return '\n'.join(textwrap.wrap(line, width=width))


def fill_line(line: str, width=30):
    """Add pads to ends of the line
    :param line: str
    :param width: maximum length of 1 row
    :return: str
    """
    return line.center(width, '-')


def colour(*args):
    """Returns a discord Colour object.
    Pass one as an argument to define colour:
        `int` match colour value.
        `str` match common colour names.
        `discord.Guild` bot's guild colour.
        `None` light grey.
    """
    arg = args[0] if args else None
    if isinstance(arg, int):
        return discord.Colour(arg)
    if isinstance(arg, str):
        colour = arg
        try:
            return getattr(discord.Colour, colour)()
        except AttributeError:
            return discord.Colour.lighter_grey()
    if isinstance(arg, discord.Guild):
        return arg.me.colour
    else:
        return discord.Colour.lighter_grey()


def permissions(*args):
    """Returns a discord Permissions object.
    Pass one as an argument to define colour:
        `int` bitcode permission value.
        `list` (dict) json formatted permission key value pairs.
        `None` discord.Permissions(121097281).
    :return: discord.Permission
    """
    arg = args[0] if args else None
    if isinstance(arg, int):
        return discord.Permissions(arg)

    if isinstance(arg, list):
        new_perms = discord.Permissions(0)
        new_perms.update(**dict.fromkeys(arg, True))
        return new_perms

    return discord.Permissions(121097281)  # default role


def make_embed(msg_type='', title=None, icon=None, content=None,
               msg_colour=None, guild=None, title_url=None,
               thumbnail='', image='', fields=None, footer=None,
               footer_icon=None, inline=False):
    """Returns a formatted discord embed object.
    Define either a type or a colour.
    Types are:
    error, warning, info, success, help.
    """

    embed_types = {
        'error': {
            'icon': 'https://i.imgur.com/juhq2uJ.png',
            'colour': 'red'
        },
        'warning': {
            'icon': 'https://i.imgur.com/4JuaNt9.png',
            'colour': 'gold'
        },
        'info': {
            'icon': 'https://i.imgur.com/wzryVaS.png',
            'colour': 'blue'
        },
        'success': {
            'icon': 'https://i.imgur.com/ZTKc3mr.png',
            'colour': 'green'
        },
        'help': {
            'icon': 'https://i.imgur.com/kTTIZzR.png',
            'colour': 'blue'
        }
    }
    if msg_type in embed_types.keys():
        msg_colour = embed_types[msg_type]['colour']
        icon = embed_types[msg_type]['icon']
    if guild and not msg_colour:
        msg_colour = colour(guild)
    else:
        if not isinstance(msg_colour, discord.Colour):
            msg_colour = colour(msg_colour)
    embed = discord.Embed(description=content, colour=msg_colour)
    if not title_url:
        title_url = discord.Embed.Empty
    if not icon:
        icon = discord.Embed.Empty
    if title:
        embed.set_author(name=title, icon_url=icon, url=title_url)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if image:
        embed.set_image(url=image)
    if fields:
        for key, value in fields.items():
            ilf = inline
            value = value if value is not None else "None"
            if not isinstance(value, str):
                ilf = value[0]
                value = value[1]
            embed.add_field(name=key, value=value, inline=ilf)
    if footer:
        footer = {'text': footer}
        if footer_icon:
            footer['icon_url'] = footer_icon
        embed.set_footer(**footer)
    return embed


def bold(msg: str):
    """Format to bold markdown text"""
    return f'**{msg}**'


def italics(msg: str):
    """Format to italics markdown text"""
    return f'*{msg}*'


def bolditalics(msg: str):
    """Format to bold italics markdown text"""
    return f'***{msg}***'


def code(msg: str):
    """Format to markdown code block"""
    return f'```{msg}```'


def pycode(msg: str):
    """Format to code block with python code highlighting"""
    return f'```py\n{msg}```'


def ilcode(msg: str):
    """Format to inline markdown code"""
    return f'`{msg}`'


def clean(msg: str):
    if isinstance(msg, bool):
        return str(msg)
    if isinstance(msg, str):
        return "None" if not msg else msg
    return "None"


def convert_to_bool(argument):
    """Determines if an argument is of type Boolean"""
    lowered = argument.lower()
    if lowered in ('yes', 'y', 'true', 't', '1', 'enable', 'on'):
        return True
    elif lowered in ('no', 'n', 'false', 'f', '0', 'disable', 'off'):
        return False
    else:
        return None


def sanitize_channel_name(name):
    """Converts a given string into a compatible discord channel name."""
    # Remove all characters other than alphanumerics,
    # dashes, underscores, and spaces
    ret = re.sub('[^a-zA-Z0-9 _\\-]', '', name)
    # Replace spaces with dashes
    ret = ret.replace(' ', '-')
    return ret.lower()


async def ask(bot, message, user_list=None, timeout=60, *, react_list=[emoji.yes, emoji.no]):
    """Template for reactions"""
    if user_list and type(user_list) != __builtins__.list:
        user_list = [user_list]

    def check(reaction, user):
        if user_list and type(user_list) is __builtins__.list:
            return (user.id in user_list) and (reaction.message.id == message.id) and (reaction.emoji in react_list)
        elif not user_list:
            return (user.id != message.author.id) and (reaction.message.id == message.id) and (
                    reaction.emoji in react_list)

    for r in react_list:
        await asyncio.sleep(0.25)
        await message.add_reaction(r)
    try:
        reaction, user = await bot.wait_for('reaction_add', check=check, timeout=timeout)
        await message.clear_reactions()
        return reaction, user
    except asyncio.TimeoutError:
        await message.clear_reactions()
        return


def format_logs(logs, prepend: str = None, append: str = None):
    """Formats a log list by prepending or appending text to each line"""
    if prepend is None and append is None:
        return logs

    formatted = []
    for log in logs:
        if prepend is not None and append is not None:
            formatted.append(f"{prepend}{log}{append}")
        elif prepend is None:
            formatted.append(f"{log}{append}")
        else:
            formatted.append(f"{prepend}{log}")

    return formatted


def find_in_dict(element, json):
    keys = element.split('.')
    rv = json
    for key in keys:
        rv = rv[key]
    return rv
