import asyncio
from datetime import datetime, timezone

import discord
from discord.ext import commands

from mobiglas import checks, utils, emoji
from mobiglas.db import get_1, save_and_get
from mobiglas.db.model.motion import Motion


class MotionCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @checks.adminchannel()
    async def motion(self, ctx, name: str):
        guild = ctx.guild

        # get channel overwrites
        ows = dict(ctx.channel.overwrites)
        motion_name = _name_check(utils.sanitize_channel_name(name))

        offer_msg = await ctx.send(embed=utils.make_embed(msg_colour=guild.me.colour, content=f"Would you like to begin the motion [**{motion_name}**]?"))

        reaction, __ = await utils.ask(self.bot, offer_msg)

        if reaction.emoji == emoji.yes:
            motion_channel = await guild.create_text_channel(motion_name, overwrites=ows)
            await motion_channel.edit(topic=motion_name)

            await ctx.send(embed=utils.make_embed(msg_colour=guild.me.colour, content=f"Creating motion channel [{motion_channel.mention}]."))

            # create motion
            eligible_nicks = []
            for member in ctx.channel.members:
                eligible_nicks.append(member.display_name)
            utils.santinize_users(eligible_nicks)  # remove bot name

            Motion(id=motion_channel.id,
                   name=motion_name,
                   creator_id=ctx.author.mention,
                   eligible_members=",".join(eligible_nicks),
                   eligible_max=len(eligible_nicks)) \
                .save(force_insert=True)

        elif reaction.emoji == emoji.no:
            await ctx.send(embed=_cancel_request())
            return
        else:
            return

        # send help
        help_screen = _get_motion_help(ctx.prefix, ctx.bot.user.avatar_url)
        await motion_channel.send(embed=help_screen)

    @motion.command()
    @checks.activemotionchannel()
    async def name(self, ctx, name: str):
        channel = ctx.channel

        motion = get_1(Motion, Motion.id == channel.id)
        # at the time of writing, we are locking down the name changes to motions that have NOT_STARTED
        if motion.status == 'NOT_STARTED':
            name = _name_check(utils.sanitize_channel_name(name))

            await ctx.send(embed=_valid_request(f"Changing motion name from **{channel.name}** to **{name}**"))
            await channel.edit(name=name, topic=name)
            motion.name = name
            motion.save()
        else:
            await ctx.send(embed=_warn_msg(f"Cannot change the name of the motion, because motion is {motion.status}."))

    @commands.command()
    @checks.activemotionchannel()
    async def detail(self, ctx, user_input=None):
        channel = ctx.channel
        guild = ctx.guild

        motion = get_1(Motion, Motion.id == channel.id)
        if not motion:
            await ctx.send(embed=_failure_notification("Failed to retrieve motion"))
            return

        detail_id = motion.detail_id
        if not user_input:
            if not detail_id:
                await ctx.send(embed=_error_msg("No detail found"))
            else:
                msg = (await ctx.fetch_message(detail_id)).embeds[0]
                await ctx.send(embed=utils.make_embed(msg_colour=msg.colour, title=channel.name, content=msg.description))
                return
        else:
            detail_msg = await ctx.send(embed=utils.make_embed(msg_colour=guild.me.colour, title=channel.name, content=user_input))
            reaction, __ = await utils.ask(self.bot, detail_msg)

            if reaction.emoji == emoji.yes:
                # delete existing
                if detail_id:
                    exiting_msg = (await ctx.fetch_message(detail_id))
                    await exiting_msg.unpin()

                await detail_msg.pin()

                motion.detail_id = detail_msg.id
                motion.save()

            elif reaction.emoji == emoji.no:
                await ctx.send(embed=_cancel_request())

    @commands.command()
    @checks.activemotionchannel()
    async def timeout(self, ctx, hours: int):
        """
            Modify the timeout
        :param ctx: context
        :param hours: user input [1,24]
        :return:
        """
        channel = ctx.channel

        if hours < 1 or hours > 24:
            await ctx.send(embed=_warn_msg("Valid options are between 1 and 24"))
        else:
            res = Motion.update(timeout=hours).where(Motion.id == channel.id).execute()
            if res == 1:
                await ctx.send(embed=_valid_request(f"Timer for this motion has been set to {hours} hour(s)."))
            else:
                await ctx.send(embed=_failure_notification("Failed to update timeout"))

    @commands.command()
    @checks.activemotionchannel()
    async def untable(self, ctx):
        channel = ctx.channel
        motion = get_1(Motion, Motion.id == channel.id)

        if not motion:
            await ctx.send(embed=_failure_notification("No motion found"))
        else:
            if motion.status != 'TABLED':
                await ctx.send(embed=_warn_msg("This motion has not been tabled."))
            else:
                await ctx.send(embed=_valid_request("This motion has been untabled."))
                await channel.edit(name=motion.name, topic=motion.name)
                motion.status = 'NOT_STARTED'
                motion.save()

    @commands.command()
    @checks.activemotionchannel()
    async def vote(self, ctx):
        channel = ctx.channel
        guild = ctx.guild

        motion = get_1(Motion, Motion.id == channel.id)
        if not motion:
            await ctx.send(embed=_failure_notification("Failed to retrieve motion"))
            return

        detail_id = motion.detail_id
        if not detail_id:
            await ctx.send(embed=_error_msg("Cannot vote on nothing"))
        else:
            msg = (await ctx.fetch_message(detail_id)).embeds[0]
            preview = await ctx.send(embed=utils.make_embed(msg_colour=msg.colour, title=channel.name, content=msg.description))
            motion.motion_id = preview.id
            motion = save_and_get(motion)
            status = motion.status  # [NOT_STARTED, IN_PROGRESS, TABLED, COMPLETE, CLOSED]

            if status == 'IN_PROGRESS':
                await ctx.send(embed=_warn_msg("Motion is already in progress."))
            elif status in ['COMPLETE', 'CLOSED']:
                await ctx.send(embed=_warn_msg("Motion has been completed. Please submit a referendum."))
            else:
                confirm = await ctx.send(embed=utils.make_embed(msg_colour=guild.me.colour, content="Are you sure you want to bring this motion to the floor?"))
                reaction, __ = await utils.ask(self.bot, confirm)

                if reaction.emoji == emoji.yes:
                    await confirm.delete()

                    motion.status = 'IN_PROGRESS'
                    motion = save_and_get(motion)

                    # update channel name to reflect a motion in-progress
                    if not channel.name.startswith("in-"):
                        new_channel_name = f"in-{motion.name}"
                        await channel.edit(name=new_channel_name, topic=new_channel_name)

                    # begin setup
                    role_board_member = discord.utils.get(ctx.guild.roles, name="Board Member")

                    # add motion to table
                    await ctx.send(embed=utils.make_embed(msg_colour=guild.me.colour,
                                                          content=f"{role_board_member.mention}. A motion has been  brought to the floor. Please review the motion and mark"
                                                          f" your vote. Motion will automatically close at {motion.end_time}"))

                    # add reactions to motion
                    for r in [emoji.yes, emoji.no, emoji.table]:
                        await asyncio.sleep(0.25)
                        await preview.add_reaction(r)

                    # wait for eligible members to vote
                    await _vote(ctx, preview, motion)

                    # count votes
                    while not _tally_complete(channel.id):
                        await asyncio.sleep(5)

                    cache_msg = await ctx.fetch_message(preview.id)
                    yea_vote = _get_voters(await cache_msg.reactions[0].users().flatten())  # unsafe reactions retrieval
                    nay_vote = _get_voters(await cache_msg.reactions[1].users().flatten())

                    motion = Motion.get_by_id(channel.id)
                    # pause motion if tabled
                    if motion.tally_tabled_user:
                        new_channel_name = f"tabled-{motion.name}"
                        await channel.edit(name=new_channel_name, topic=new_channel_name)
                        await ctx.send(embed=_warn_msg(f"{role_board_member.mention}, {motion.tally_tabled_user} has tabled the motion. \nMotion is put on pause."))
                        return
                    else:
                        yeas = ', '.join(list(set(yea_vote)))  # poor mans dedup
                        motion.tally_yeas = yeas

                        nays = ', '.join(list(set(nay_vote)))
                        motion.tally_nays = nays

                        tally_members = f"The motion has completed. \n" \
                            f"Those in favor [{yeas}].\n " \
                            f"Those against [{nays}]"

                        if motion.tally_yea_count > motion.eligible_max / 2:
                            tally = utils.make_embed(msg_colour=discord.Colour.green(), content=f"{role_board_member.mention}.\nThe **yeas** have it.\n{tally_members}")
                            new_channel_name = f"passed-{motion.name}"
                            await channel.edit(name=new_channel_name, topic=new_channel_name)
                        elif motion.tally_nay_count > motion.eligible_max / 2:
                            tally = utils.make_embed(msg_colour=discord.Colour.red(), content=f"{role_board_member.mention}.\nThe **nays** have it.\n{tally_members}")
                            new_channel_name = f"failed-{motion.name}"
                            await channel.edit(name=new_channel_name, topic=new_channel_name)
                        else:
                            tally = _error_msg(f"{role_board_member.mention}, {motion.timeout} hours have passed since motion came to floor.\n Motion has **failed** to pass a majority vote.")
                            new_channel_name = f"failed-{motion.name}"
                            await channel.edit(name=new_channel_name, topic=new_channel_name)
                            motion.status = 'COMPLETE'

                        final_notice = await ctx.send(embed=tally)
                        await final_notice.pin()

                        await ctx.send(f"{motion.creator_id}, the motion has ended. Please document,  then `!motion close` this channel.")

                        motion.save()

                elif reaction.emoji == emoji.no:
                    await ctx.send(embed=_cancel_request())
                else:
                    return

    # todo: resume vote -- after bot outage

    @commands.command()
    @checks.activemotionchannel()
    async def close(self, ctx):
        channel = ctx.channel
        guild = ctx.guild

        confirm = await ctx.send(embed=utils.make_embed(msg_colour=guild.me.colour,
                                                        content="Are you sure you want to close this motion? "
                                                        f"Once closed it cannot be recovered."))
        reaction, __ = await utils.ask(self.bot, confirm)

        if reaction.emoji == emoji.yes:
            await ctx.send(embed=_valid_request("Request confirmed. Deleting in 5 minutes."))
            await asyncio.sleep(60 * 5)
            await channel.delete()
            motion = get_1(Motion, Motion.id == channel.id)
            motion.status = 'CLOSED'
            motion.save()

        else:
            await ctx.send(embed=_cancel_request())


def _warn_msg(msg: str):
    return utils.make_embed(msg_colour=discord.Colour.orange(), content=msg)


def _error_msg(msg: str):
    return utils.make_embed(msg_colour=discord.Colour.red(), content=msg)


def _failure_notification(msg: str):
    return _error_msg(f"Error: {msg}. Please contact a moderator for assistance.")


def _cancel_request():
    return _error_msg("Request canceled.")


def _valid_request(msg):
    return utils.make_embed(msg_colour=discord.Colour.green(), content=msg)


def _name_check(name: str):
    tmp = name.lower().replace(' ', '-')
    if not tmp.startswith('motion-'):
        return f"motion-{name}"
    else:
        return name


def _tally_complete(channel_id):
    """
        A motion is considered complete if all votes are accounted for OR
        the timeout has passed with a majority vote.
    :param channel_id: Long
    :return: Boolean
    """
    motion = get_1(Motion, channel_id)
    end_time = motion.end_time.replace(tzinfo=timezone.utc).timestamp()
    if motion.status == 'COMPLETE':
        return True
    if end_time > datetime.now().timestamp():
        return True
    return False


async def _vote(ctx, message, motion, timeout=86400, react_list=[emoji.yes, emoji.no, emoji.table]):
    """
        This function is to watch for reactions and record them as they are received.

        Note:   We were forced to follow this convention, because the Message.reactions() was not updated in real-time.
                Very likely it is async.
    :param ctx:
    :param message: Message
    :param motion: Motion
    :param timeout: Long (default=24 hours)
    :param react_list: List[Emoji's]
    """
    member_list = motion.eligible_members.split(",")

    def check(reaction, user):
        return (user.nick in member_list) and (reaction.message.id == message.id) and (reaction.emoji in react_list)

    # add reactions to motion
    for r in react_list:
        await asyncio.sleep(0.25)
        await message.add_reaction(r)

    try:
        buffer = Motion.get_by_id(motion.id)
        while buffer.status != 'COMPLETE':
            # race condition: if user selects a vote too fast, it won't count
            await asyncio.sleep(0.25)
            reaction, user = await ctx.bot.wait_for('reaction_add', check=check, timeout=timeout)
            # currently there is no way to wait_for multiple reactions such as 'reaction_add,reaction_remove'
            # todo: implement own sync callback to handle both cases (post-mvp)

            if reaction.emoji == emoji.table:
                buffer.tally_tabled_user = user.nick  # a bit wonky, todo: normalizer later
                buffer.save()
                return
            elif reaction.emoji == emoji.yes:
                buffer.tally_yea_count = reaction.count - 1
            elif reaction.emoji == emoji.no:
                buffer.tally_nay_count = reaction.count - 1

                # save_and_get() appears to be unsafe with this thread... todo: explore
            buffer.save()
            buffer = Motion.get_by_id(motion.id)
        return
    except asyncio.TimeoutError:
        pass


def _get_voters(users):
    """
        Gets the list of voters excluding the bot
    :param users: List[String] of user names
    :return: List[String]
    """
    voters = []
    for vote in users:
        if vote.bot:
            continue
        voters.append(utils.get_member_nickname(vote))
    return voters


def _get_motion_help(prefix, avatar):
    help_embed = discord.Embed(colour=discord.Colour.lighter_grey())
    help_embed.set_author(name="Motion Help", icon_url=avatar)
    help_embed.add_field(
        name="Key",
        value="<> required arguments, [] optional arguments, (D) default",
        inline=False)

    help_embed.add_field(
        name="Motion MGMT Commands",
        value=(
            f"`{prefix}name \"<motion name>\"`\n"
            f"`{prefix}detail \"<details>\"`\n"
            f"`{prefix}timeout \"<1-24> hours\"`\n"
            f"`{prefix}vote`\n"
            f"`{prefix}untable`\n"
            f"`{prefix}close`\n"
            f"`{prefix}help`\n"))
    help_embed.add_field(
        name="Defaults",
        value=(
            "`motion-...`\n"
            "\n"
            "`24`\n"
            "\n"
            "\n"
            "\n"
            "\n"))

    return help_embed


def setup(bot):
    bot.add_cog(MotionCommands(bot))
