import asyncio

from datetime import datetime, timedelta
import discord
from discord.ext import commands

from mobiglas import checks, utils, emoji


class MotionCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @checks.adminchannel()
    async def motion(self, ctx, name: str):
        guild = ctx.guild
        guild_dict = ctx.bot.guild_dict

        # get channel overwrites
        ows = dict(ctx.channel.overwrites)
        motion_name = _name_check(utils.sanitize_channel_name(name))

        offer_msg = await ctx.send(embed=utils.make_embed(msg_colour=guild.me.colour,
                                                          content=f"Would you like to begin the motion [**{motion_name}**]?"))

        reaction, __ = await utils.ask(self.bot, offer_msg)

        if reaction.emoji == emoji.yes:
            motion_channel = ctx.motion_channel = await guild.create_text_channel(motion_name, overwrites=ows)
            await motion_channel.edit(topic=motion_name)

            await ctx.send(embed=utils.make_embed(msg_colour=guild.me.colour,
                                                  content=f"Creating motion channel [{ctx.motion_channel.mention}]."))

            guild_dict[guild.id]['motion'][motion_channel.id] = {
                'active': True,
                'author': ctx.author,
                'detail': None,
                'in_motion': None,
                'timer': 24,  # number of hours to wait before automatically closing the polls
                'motion_start_time': None,
                'motion_end_time': None,
                'complete': {
                    'status': False,
                    'yea': [],
                    'nay': [],
                    'close': False
                }
            }

        elif reaction.emoji == emoji.no:
            await ctx.send(embed=utils.make_embed(msg_colour=discord.Colour.red(),
                                                  content=f"Acknowledged, will not create motion [{motion_name}]."))

        # send help
        help_embed = _get_motion_help(ctx.prefix, ctx.bot.user.avatar_url)
        await ctx.motion_channel.send(embed=help_embed)

    # todo: check to see if it's the creator of the channel
    @motion.command()
    @checks.activemotionchannel()
    async def name(self, ctx, name: str):
        channel = ctx.channel

        name = _name_check(utils.sanitize_channel_name(name))

        await ctx.send(f"Changing motion name from **{channel.name}** to **{name}**")
        await channel.edit(name=name, topic=name)

    @motion.command()
    @checks.activemotionchannel()
    async def detail(self, ctx, details=None):
        channel = ctx.channel
        guild = ctx.guild
        motion_dict = ctx.bot.guild_dict[guild.id]['motion'][channel.id]

        if not details:
            if not motion_dict['detail']:
                await ctx.send(embed=utils.make_embed(msg_colour=discord.Colour.red(),
                                                      content="No detail found."))
            else:
                msg = (await ctx.fetch_message(motion_dict['detail'])).embeds[0]
                await ctx.send(embed=utils.make_embed(msg_colour=msg.colour,
                                                      title=channel.name,
                                                      content=msg.description))
                return
        else:
            detail_msg = await ctx.send(embed=utils.make_embed(msg_colour=guild.me.colour,
                                                               title=channel.name,
                                                               content=details))
            reaction, __ = await utils.ask(self.bot, detail_msg)

            if reaction.emoji == emoji.yes:
                # delete existing
                if motion_dict['detail']:
                    exiting_msg = (await ctx.fetch_message(motion_dict['detail']))
                    await exiting_msg.unpin()

                await detail_msg.pin()
                motion_dict['detail'] = detail_msg.id

    @motion.command()
    @checks.activemotionchannel()
    async def timer(self, ctx, hours: int):
        channel = ctx.channel
        guild = ctx.guild
        motion_dict = ctx.bot.guild_dict[guild.id]['motion'][channel.id]

        if hours < 1 or hours > 24:
            await ctx.send(embed=utils.make_embed(msg_colour=discord.Colour.red(),
                                                  content="Valid options are between 1 and 24"))
        else:
            motion_dict['timer'] = hours
            await ctx.send(embed=utils.make_embed(msg_colour=discord.Colour.green(),
                                                  content=f"Timer for this motion has been set to {hours}"))

    @motion.command()
    @checks.activemotionchannel()
    async def vote(self, ctx):
        channel = ctx.channel
        guild = ctx.guild
        motion_dict = ctx.bot.guild_dict[guild.id]['motion'][channel.id]

        if not motion_dict['detail']:
            await ctx.send(embed=utils.make_embed(msg_colour=guild.me.colour,
                                                  content="Cannot vote on nothing."))
        else:
            motion = (await ctx.fetch_message(motion_dict['detail'])).embeds[0]
            preview = await ctx.send(embed=utils.make_embed(msg_colour=motion.colour,
                                                            title=channel.name,
                                                            content=motion.description))
            if motion_dict['in_motion']:
                await ctx.send(embed=utils.make_embed(msg_colour=discord.Colour.red(),
                                                      content="Motion in progress."))
            else:

                confirm = await ctx.send(embed=utils.make_embed(msg_colour=guild.me.colour,
                                                                content="Are you sure you want to bring this motion to the floor?"))
                reaction, __ = await utils.ask(self.bot, confirm)

                if reaction.emoji == emoji.yes:
                    await confirm.delete()
                    ts = datetime.utcnow()
                    motion_dict['motion_start_time'] = ts.timestamp() * 1e3
                    motion_dict['motion_end_time'] = (ts + timedelta(hours=motion_dict['timer'])).timestamp() * 1e3
                    motion_dict['in_motion'] = preview.id
                    in_motion_channel_name = f"in-{channel.name}"
                    await channel.edit(name=in_motion_channel_name, topic=in_motion_channel_name)
                    role_board_member = discord.utils.get(ctx.guild.roles, name="Board Member")
                    await ctx.send(embed=utils.make_embed(msg_colour=guild.me.colour,
                                                          content=f"{role_board_member.mention}. A motion has been"
                                                          " brought to the floor. Please review the motion and mark"
                                                          " your vote. Motion will automatically close at #TODO"))  # add motion_end_time
                    board_members = role_board_member.members
                    await _vote(ctx, preview, user_list=board_members)

                    # count votes
                    timer = motion_dict['timer'] * 60 * 60  # hours * minutes * seconds
                    await asyncio.sleep(timer)
                    cache_msg = await ctx.fetch_message(preview.id)
                    yea_vote, cyea = _count_votes(await cache_msg.reactions[0].users().flatten())
                    nay_vote, cnay = _count_votes(await cache_msg.reactions[1].users().flatten())
                    table_vote, ctable = _count_votes(await cache_msg.reactions[2].users().flatten())

                    # pause motion if tabled
                    if ctable > 0:
                        motion_dict['in_motion'] = None
                        default_motion_channel_name = channel.name.replace('in-', '')
                        await channel.edit(name=default_motion_channel_name, topic=default_motion_channel_name)
                        await ctx.send(embed=utils.make_embed(msg_colour=discord.Colour.red(),
                                                              content=f"{role_board_member.mention}, {table_vote[0]}"
                                                              " has tabled the  motion. \nMotion is put on pause."))
                        return
                    else:
                        motion_dict['complete']['yea'] = yea_vote
                        motion_dict['complete']['nay'] = nay_vote

                        tally_members = f"The motion has completed. \n" \
                            f"Those in favor [{', '.join(yea_vote)}].\n " \
                            f"Those against [{', '.join(nay_vote)}]"

                        if cyea + 2 > 2:
                            tally = utils.make_embed(msg_colour=discord.Colour.green(),
                                                     content=f"{role_board_member.mention}.\nThe yeas have it.\n{tally_members}")
                            pass_motion_channel_name = channel.name.replace('in-', 'passed-')
                            await channel.edit(name=pass_motion_channel_name, topic=pass_motion_channel_name)
                        elif cnay + 2 > 2:
                            tally = utils.make_embed(msg_colour=discord.Colour.red(),
                                                     content=f"{role_board_member.mention}.\nThe nays have it.\n{tally_members}")
                            failed_motion_channel_name = channel.name.replace('in-', 'failed-')
                            await channel.edit(name=failed_motion_channel_name, topic=failed_motion_channel_name)
                        else:
                            tally = utils.make_embed(msg_colour=discord.Colour.red(),
                                                     content=f"{role_board_member.mention}, 24 hours have passed since "
                                                     f"motion came to floor.\n Motion has failed to pass a majority vote.")
                            failed_motion_channel_name = channel.name.replace('in-', 'failed-')
                            await channel.edit(name=failed_motion_channel_name, topic=failed_motion_channel_name)

                        motion_dict['complete']['status'] = True
                        final_notice = await ctx.send(embed=tally)
                        await final_notice.pin()

                        await ctx.send(f"{motion_dict['author'].mention}, the motion has ended. Please document, "
                                       "then `!motion close` this channel.")

    @motion.command()
    @checks.activemotionchannel()
    async def close(self, ctx):
        channel = ctx.channel
        guild = ctx.guild
        motion_dict = ctx.bot.guild_dict[guild.id]['motion'][channel.id]

        confirm = await ctx.send(embed=utils.make_embed(msg_colour=guild.me.colour,
                                                        content="Are you sure you want to close this motion? "
                                                        f"Once closed it cannot be recovered."))
        reaction, __ = await utils.ask(self.bot, confirm)

        if reaction.emoji == emoji.yes:
            # async service later will consume and send msgs to backend for storage
            motion_dict['complete']['close'] = True
            await ctx.send(embed=utils.make_embed(msg_colour=discord.Colour.green(),
                                                  content="Request confirmed. Deleting in 20 seconds."))
            # content="Request confirmed. Deleting in 5 minutes."))
            await asyncio.sleep(20)
            await channel.delete()
            del motion_dict


def _name_check(name: str):
    tmp = name.lower().replace(' ', '-')
    if not tmp.startswith('motion-'):
        return f"motion-{name}"
    else:
        return name


async def _vote(ctx, message, user_list, timeout=86400, react_list=[emoji.yes, emoji.no, emoji.table]):
    if isinstance(user_list[0], discord.Member):
        tmp_list = []
        for user in user_list:
            tmp_list.append(user.id)
        user_list = tmp_list

    def check(reaction, user):
        return (user.id in user_list) and (reaction.message.id == message.id) and (reaction.emoji in react_list)

    for r in react_list:
        await asyncio.sleep(0.25)
        await message.add_reaction(r)

    try:
        votes = 3
        # votes = 0
        while votes < len(user_list) - 1:
            await asyncio.sleep(0.25)
            reaction, user = await ctx.bot.wait_for('reaction_add', check=check, timeout=timeout)

            if reaction == emoji.table:
                return
            votes += 1
        return
    except asyncio.TimeoutError:
        pass


def _count_votes(votes):
    voters = []
    for vote in votes:
        if vote.bot:
            continue
        voters.append(utils.get_member_nickname(vote))
    return voters, len(voters)


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
            f"`{prefix}motion name \"<motion name>\"`\n"
            f"`{prefix}motion detail \"<details>\"`\n"
            f"`{prefix}motion timer \"<1-24> hours\"`\n"
            f"`{prefix}motion vote`\n"
            f"`{prefix}motion close`\n"
            f"`{prefix}motion help`\n"))
    help_embed.add_field(
        name="Defaults",
        value=(
            "`motion-...`\n"
            "\n"
            "`24`\n"
            "\n"
            "\n"
            "\n"))

    return help_embed


def setup(bot):
    bot.add_cog(MotionCommands(bot))
