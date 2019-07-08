import re

import discord
import rocksdb
from discord.ext import commands

from mobiglas import checks
from mobiglas.rocks.datastore import DataStore
from mobiglas.rocks.filters import PrefixFilter


class System(commands.Cog):
    def __init__(self, bot):
        ds = DataStore()
        self.bot = bot
        self.ds = ds

    @commands.command()
    @checks.adminchannel()
    async def clean_all(self, ctx):
        guild = ctx.guild
        _clean(self.ds, ctx, str(guild.id))

    @commands.command()
    @checks.adminchannel()
    async def dump(self, ctx):
        lst = self.ds.full_scan()

        for i in lst:
            print(i)


def _clean(ds: DataStore, ctx, prefix: str, force: bool = False):
    lst = PrefixFilter.find(prefix, ds.scan())

    channel_key_set = _get_channel_key_set(lst)

    cleanup_request = rocksdb.WriteBatch()
    for cid in channel_key_set:
        channel = discord.utils.get(ctx.guild.channels, id=cid)
        if channel is not None and not force:
            continue

        # delete ds entry if the guild.channel no longer exists
        channel_id = str(cid)
        for i in lst:
            if channel_id in i:
                print(f"Deleting inactive entry {i}.")
                cleanup_request.delete(ds.prepare_key(i))

    ds.batch(cleanup_request)


def _get_channel_key_set(lst):
    channel_key_set = set()
    for key in lst:
        cid_str = _get_channel_id(key)
        if cid_str is None:
            continue
        key = int(cid_str)
        channel_key_set.add(key)
    return channel_key_set


def _get_channel_id(src: str):
    channel_id_regex = re.compile(r'(\d*)(\.)(\w*)(\.)(\d*)')
    match = channel_id_regex.match(src)
    if match is None:
        pass
    else:
        return match.group(5)


def setup(bot):
    bot.add_cog(System(bot))
