import random

from discord import Colour
from discord import Embed
from discord.ext import commands
from commands.Amount_converter import Amount
from commands.Coin_converter import CoinType
from economy.Economy import amount_to_string
from economy.Economy import amount_valid


class OverUnder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Usage = "The over/under commands"

    @commands.command(name="over")
    async def over(self, ctx, type: CoinType, amount: Amount):
        amount_valid(self.bot, ctx.author.id, amount, type)
        self.bot.wagered(ctx.author.id, amount, type)
        rolled = random.randint(0, 100)
        has_won = rolled >= 45

        if has_won:
            embed = Embed(colour=Colour.green())
        else:
            embed = Embed(colour=Colour.red())

        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Over/Under game",
                        value=f"Number is {rolled}. You {'won' if has_won else 'lost'} {amount_to_string(amount)} {type.format_string()}"
                        )

        await ctx.send(embed=embed)
        if has_won:
            self.bot.update_amount(ctx.author.id, (amount), type)
        else:
            self.bot.update_amount(ctx.author.id, -amount, type)


    @commands.command(name="under")
    async def under(self, ctx, type: CoinType, amount: Amount):
        amount_valid(self.bot, ctx.author.id, amount, type)
        self.bot.wagered(ctx.author.id, amount, type)
        rolled = random.randint(0, 100)
        has_won = rolled <= 50

        if has_won:
            embed = Embed(colour=Colour.green())
        else:
            embed = Embed(colour=Colour.red())

        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Over/Under game",
                        value=f"Number is {rolled}. You {'won' if has_won else 'lost'} {amount_to_string(amount)} {type.format_string()}."
                        )

        await ctx.send(embed=embed)
        if has_won:
            self.bot.update_amount(ctx.author.id, (amount), type)
        else:
            self.bot.update_amount(ctx.author.id, -amount, type)

    @over.error
    @under.error
    async def info_error(self, ctx, error):
        embed = Embed(colour=Colour.red())
        embed.set_footer(text="Usage: ![over | under] [rs3 | 07] amount")
        embed.add_field(name='Error', value=error.args[0].replace("Command raised an exception: Exception: ", ""))
        await ctx.send(embed=embed)