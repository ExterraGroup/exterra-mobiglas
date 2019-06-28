import discord
from discord.ext import commands

from mobiglas import utils, checks


class Raid(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def wait_for_cmd(self, console_channel, user, command_name):

        # build check relevant to command
        def check(c):
            if not c.channel == console_channel:
                return False
            if not c.author == user:
                return False
            if c.command.name == command_name:
                return True
            return False

        # wait for the command to complete
        cmd_ctx = await self.bot.wait_for(
            'command_completion', check=check, timeout=100)

        return cmd_ctx

    def get_overwrites(self, guild, member):
        return {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False),
            member: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_channels=True),
            guild.me: discord.PermissionOverwrite(
                read_messages=True)
        }

    @commands.group(invoke_without_command=True)
    # todo: checks.permissions('raid_operators')
    @checks.adminchannel()
    async def raid(self, ctx):
        user = ctx.author
        guild = ctx.guild

        # get channel overwrites
        ows = self.get_overwrites(guild, user)

        # create console channel
        name = utils.sanitize_channel_name(user.display_name + "-console")

        ctx.raid_config_channel = await guild.create_text_channel(
            name, overwrites=ows)  # this is permissions for viewing the channel. explore later

        await ctx.message.delete()
        await ctx.send((f"Launching raid configuration console {ctx.raid_config_channel.mention}. "
                        f"This message will self destruct in 20 seconds"), delete_after=20.0)

        # ctx.raid_dict_map['raid']['channel'] = {
        #     'id': ctx.raid_config_channel.id,
        #     'operation': Operation(ctx, 'test-op')
        # }
        await self.raid_option(ctx)

    async def raid_option(self, ctx):

        raid_config_channel = ctx.raid_config_channel
        raid_channel = None

        # display help commands
        help_embed = await get_raid_config_help(ctx.prefix, ctx.bot.user.avatar_url)
        await raid_config_channel.send(embed=help_embed)

        return

    # @console.command()
    # async def raid(self, ctx):
    #     ctx.send("blah")

    @raid.command()
    async def name(self, ctx, op_name: str):
        return


async def get_raid_config_help(prefix, avatar, user=None):
    help_embed = discord.Embed(colour=discord.Colour.lighter_grey())
    help_embed.set_author(name="Raid Coordination Help", icon_url=avatar)
    help_embed.add_field(
        name="Key",
        value="<> required arguments, [] optional arguments, (D) default",
        inline=False)

    help_embed.add_field(
        name="Raid MGMT Commands",
        value=(
            f"`{prefix}name \"<raid name>\"`\n"
            f"`{prefix}min_commanders <num>`\n"
            f"`{prefix}max_commanders <num>`\n"
            f"`{prefix}min_players <num>`\n"
            f"`{prefix}max_players <num>`\n"
            f"`{prefix}comms <comms>`\n"
            f"`{prefix}details \"<info>\"`\n"
            f"`{prefix}link <url>`\n"
            f"`{prefix}date <date>`\n"
            f"`{prefix}commander_assignment <style>`\n"
            f"`{prefix}!create`\n"
            f"`{prefix}!close`\n"
            "**RSVP**\n"
            f"`{prefix}(i/c/h)...\n"
            "[total]...\n"
            "[team counts]`\n"
            "**Lists**\n"
            f"`{prefix}list [status]`\n"
            f"`{prefix}list [status] tags`\n"
            f"`{prefix}list teams`\n\n"
            f"`{prefix}starting [team]`"))
    help_embed.add_field(
        name="Defaults",
        value=(
            "`Operation Redacted`\n"
            "`1`\n"
            "`1`\n"
            "`2`\n"
            "`2`\n"
            "`(D)TeamSpeak|Discord`\n"
            "`redacted`\n"
            "`redacted`\n"
            "`yyyy-mm-ddT00:00`\n"
            "`(D)fifo|choice|random`\n"
            "\n"
            "\n"))

    if not user:
        return help_embed
    await user.send(embed=help_embed)


def setup(bot):
    bot.add_cog(Raid(bot))
