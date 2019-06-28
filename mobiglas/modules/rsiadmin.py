import discord
from discord.ext import commands

from mobiglas import checks
from mobiglas.exterragroup.scorgsite import get_user_roles, get_citizen, get_discord_role_configs
from mobiglas.exterragroup.utils import member_status, format_orgs, sort_roles, align_nickname, clear_roles, \
    create_guild_role, get_rank, get_roles, get_certs
from mobiglas.utils import fill_line, find_guild_username, print_logs, clean, get_member_nickname


class RsiAdminCommands(commands.Cog):
    """
        Bot Commands:   RSI related
        Permissions:    'Board Member' Role
        Channels:       Admin channels
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    @checks.adminchannel()
    async def sync_roles(self, ctx):
        role_datum = get_discord_role_configs()
        logger = await create_guild_role(ctx, role_datum['roles'], role_datum['certifications'], role_datum['ranks'])

        await print_logs(ctx, logger)
        return

    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    @checks.adminchannel()
    async def sync_member(self, ctx, handle: str):
        logger = []

        # find member based on guild username or guild nickname
        guild_member = find_guild_username(ctx, handle)
        if guild_member is None:
            await ctx.send(f"User [{handle}] **not** found.")
            return

        # get permissions from source of truth - site controlled
        user_datum = get_user_roles(guild_member.name)

        status = member_status(user_datum)
        if not status[1]:
            logger.append(f"**Error**: User [{handle}] is not a registered member on the site.")
            logger.append(f"Member Status: **{status[0]}**")
            logger.extend(await clear_roles(ctx, guild_member))

            await print_logs(ctx, logger)
            return

        logger.extend(await sort_roles(ctx, user_datum, guild_member))
        logger.extend(await align_nickname(user_datum, guild_member))

        await print_logs(ctx, logger)
        return

    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    @checks.adminchannel()
    async def dossier(self, ctx, handle: str):
        description = [
            fill_line("Dossier", width=60),
            "This is document has been marked with classifications:",
            "[U]  // Unclassified",
            "[P]  // Public Trust",
            "[S]  // Secret",
            "[TS] // Top Secret"
        ]
        dossier = discord.Embed(colour=discord.Colour(0xefc0b8),
                                description='\n'.join(description))

        # find member based on guild username or guild nickname
        guild_member = find_guild_username(ctx, handle)
        if guild_member is None:
            await ctx.send(f"User [{handle}] **not** found.")
            return

        member, rsi_citizen = get_citizen(get_member_nickname(guild_member))
        if rsi_citizen['avatar'] is None:
            await ctx.send("Error: handle [" + handle + "] is not a RSI citizen.")
            return

        dossier.set_thumbnail(url=rsi_citizen['avatar'])
        dossier.set_author(name=rsi_citizen['handle'],
                           url=rsi_citizen['url'],
                           icon_url=rsi_citizen['avatar'])

        citizen_intel = [
            f"[U] **Handle:** {handle}",
            f"[U] **User Name:** {rsi_citizen['username']}",
            f"[U] **Citizen Record:** {str(rsi_citizen['citizenRecord'])}",
            f"[U] **Enlisted:** {rsi_citizen['enlisted']}",
            f"[U] **Title:** {clean(rsi_citizen['title'])}",
            f"[U] **Bio:** {clean(rsi_citizen['bio'])}",
            f"[U] **Location:** {clean(rsi_citizen['location'])}"
        ]
        if rsi_citizen['languages'] is not None:
            citizen_intel.append(f"[U] **Languages:** {', '.join(rsi_citizen['languages'])}")

        dossier.add_field(name=f"Citizen Intel",
                          value='\n'.join(citizen_intel))

        if member is not None:
            other = [f"[P] **Member Status:** {member_status(member)[0]}"]
            if member['isHidden']:
                other.append("[TS] **Org Visibility:** Hidden")
            if member['isStaff']:
                other.append("[P] **Staff:** True")
            if member['isAdmin']:
                other.append("[S] **Admin:** True")

            other.extend([
                f"[P] **Rank:** {clean(get_rank(member))}",
                f"[P] **Roles:** {clean(get_roles(member))}",
                f"[P] **Certifications:** {clean(get_certs(member))}"
            ])

            dossier.add_field(name=f"Member Intel",
                              value='\n'.join(other))

        dossier.add_field(name=f"Associated Orgs",
                          value=''.join(format_orgs(rsi_citizen)))

        await ctx.send(embed=dossier)
        return


def setup(bot):
    bot.add_cog(RsiAdminCommands(bot))
