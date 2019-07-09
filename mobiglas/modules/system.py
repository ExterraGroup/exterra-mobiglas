import asyncio

import discord
from discord.ext import commands

from mobiglas import checks, utils, emoji
from mobiglas.db import get_1
from mobiglas.db.model.motion import Motion


class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.adminchannel()
    async def prune(self, ctx, user_input):
        """
            prune is used to delete channels without a category that contains {user_input}
        :param ctx:
        :param user_input:
        """
        guild = ctx.guild
        channels = guild.channels

        purge_list = []
        purge_list_with_names = []
        for channel in channels:
            # only prune channels that are not active
            if user_input in channel.name and not channel.category_id and not get_1(Motion, Motion.id == channel.id):
                purge_list.append(channel)
                purge_list_with_names.append(channel.name)

        if len(purge_list) > 0:
            confirm = await ctx.send(embed=utils.make_embed(msg_colour=discord.Colour.orange(),
                                                            content="*Are you sure you want to purge the following channels?*\n" +
                                                                    "\n".join(purge_list_with_names)))

            reaction, __ = await utils.ask(self.bot, confirm)

            if reaction.emoji == emoji.yes:
                for channel in purge_list:
                    await ctx.send(f"   > Deleting channel [{channel.name}].")
                    await channel.delete()
                    await asyncio.sleep(0.25)
                await ctx.send(f"   > Complete.")
            else:
                await ctx.send(embed=utils.make_embed(msg_colour=discord.Colour.red(),
                                                      content="Request canceled."))
        else:
            await ctx.send("Nothing to prune.")

    # todo: sync command
    ## this should delete all stale motion channels

    @commands.command()
    @checks.adminchannel()
    async def dump(self, ctx):
        lst = self.ds.full_scan()

        for i in lst:
            print(i)


def setup(bot):
    bot.add_cog(System(bot))
