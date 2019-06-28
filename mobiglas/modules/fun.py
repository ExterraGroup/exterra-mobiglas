from discord.ext import commands


class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def gib(self, ctx):
        """ Posts a gib '༼ つ ◕_◕ ༽つ' """
        await ctx.send('༼ つ ◕_◕ ༽つ')


def setup(bot):
    bot.add_cog(FunCommands(bot))
