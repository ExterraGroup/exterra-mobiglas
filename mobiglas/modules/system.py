import asyncio

import discord
from discord.ext import commands

from mobiglas import checks, utils, emoji


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
            if user_input in channel.name and not channel.category_id:
                purge_list.append(channel)
                purge_list_with_names.append(channel.name)

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
