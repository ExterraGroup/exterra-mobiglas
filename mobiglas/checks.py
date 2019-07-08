import discord.utils
from discord.ext import commands

from mobiglas.db import get_1
from mobiglas.db.model.motion import Motion
from .config import settings


def check_is_owner(ctx):
    author = ctx.author.id
    return author in settings.bot.owners


def check_permissions(ctx, perms):
    if not perms:
        return False
    ch = ctx.channel
    author = ctx.author
    resolved = ch.permissions_for(author)
    return all((getattr(resolved, name, None) == value for (name, value) in perms.items()))


def role_or_permissions(ctx, check, **perms):
    if check_permissions(ctx, perms):
        return True
    ch = ctx.channel
    author = ctx.author
    if ch.is_private:
        return False
    role = discord.utils.find(check, author.roles)
    return role is not None


# Configuration
def check_raidchannel(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel
    guild = ctx.guild
    raid_channels = ctx.bot.guild_dict[guild.id]['raidchannel_dict'].keys()
    return channel.id in raid_channels


def check_adminchannel(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel.id
    return channel in settings.bot.admin_channels


def check_activemotionchannel(ctx):
    if ctx.guild is None:
        return False

    return False if not get_1(Motion, Motion.id == ctx.channel.id) else True


# Decorators
def is_owner():
    def predicate(ctx):
        return check_is_owner(ctx)

    return commands.check(predicate)


def adminchannel():
    def predicate(ctx):
        return check_adminchannel(ctx)

    return commands.check(predicate)


def raidchannel():
    def predicate(ctx):
        return check_raidchannel(ctx)

    return commands.check(predicate)


def activemotionchannel():
    def predicate(ctx):
        return check_activemotionchannel(ctx)

    return commands.check(predicate)


# todo: below
def can_react(ctx):
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.permissions_for(ctx.guild.me).add_reactions
