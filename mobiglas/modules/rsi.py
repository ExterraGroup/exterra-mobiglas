import discord
from discord.ext import commands

from mobiglas import utils, emoji
from mobiglas.exterragroup.scorgsite import get_possible_ships


class RsiCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def ship(self, ctx, keyword: str):
        """
            Search for ship in the database using keyword.
            Maximum of 10 results.
            Searches resulting in more than 10 results will throw an error.
        :param ctx:
        :param keyword:
        :return: Ship Info
        """
        try:
            ship = get_possible_ships(keyword)
            matches = len(ship)
            color = discord.Colour(0xC2E3DC)

            if matches == 0:
                await ctx.warning("No matches found.")
                return

            if matches > 10:
                # bad_query_msg = utils.make_embed(msg_colour=color,
                #                                  content=f"**Keyword:** {keyword} returned {matches} results. Be more specific.")
                await ctx.warning(f"**Keyword** [{keyword}] returned {matches} results. Be more specific.")
                return

            if matches == 1:
                await ctx.send(embed=craft_ship_info(color=color, ship=ship[0]))
                return

            if matches > 1:
                manufacturer = ship[0]['manufacturer']['name']

                title = f"**Manufacturer:** {manufacturer}\n\n**Keyword:** {keyword} returned {matches} results.\n\n\n"

                content_builder = [title]
                for i in range(matches):
                    model = ship[i]['name']
                    content_builder.append(f"{emoji.numbers_unicode_list[i]:<{20}}: {model}\n")

                offer_msg = await ctx.embed(colour=color, description=''.join(content_builder))

                reaction, __ = await utils.ask(self.bot, offer_msg, react_list=emoji.numbers_unicode_list[:matches])

                pos = emoji.get_index(emoji=reaction.emoji)
                await ctx.send(embed=craft_ship_info(color=color, ship=ship[pos - 1]))
                return
        except:
            await ctx.warning("Try again.")


def craft_ship_info(color, ship):
    manufacturer = ship['manufacturer']['name']
    img = ship['images']['store_large']
    name = ship['name']
    ship_url = ship['url']
    focus = ship['focus']
    length = ship['length']
    height = ship['height']
    beam = ship['beam']
    min_crew = ship['minCrew']
    max_crew = ship['maxCrew']
    cargo_capacity = ship['cargoCapacity']
    pledge_cost = ship['pledgeCost']

    return utils.make_embed(msg_colour=color,
                            content=f"[{manufacturer} - {name}]({ship_url})",
                            fields={
                                'Focus': focus,
                                'Length': str(length),
                                'Height': str(height),
                                'Beam': str(beam),
                                'Cargo Capacity': str(cargo_capacity),
                                'Min Crew': str(min_crew),
                                'Max Crew': str(max_crew),
                                'Price': str(pledge_cost)
                            },
                            inline=True,
                            image=img)


def setup(bot):
    bot.add_cog(RsiCommands(bot))
