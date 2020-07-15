import random

from discord import Colour
from discord import Embed
from discord.ext import commands
from commands.Amount_converter import Amount
from commands.Coin_converter import CoinType
from economy.Economy import amount_to_string
from economy.Economy import amount_valid


async def roll(bot, ctx, amount, type, chance, multiplier):
    amount_valid(bot, ctx.author.id, amount, type)
    bot.wagered(ctx.author.id, amount, type)

    rolled = bot.random_number(ctx.author.id)
    has_won = rolled > chance

    if has_won:
        embed = Embed(colour=Colour.green())
    else:
        embed = Embed(colour=Colour.red())

    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.add_field(name="Dice game",
                    value=f"Rolled {rolled} out of 100. You {'won' if has_won else 'lost'} {amount_to_string((amount * multiplier) - amount) if has_won else amount_to_string(amount)} {type.format_string()}"
                    )

    embed.set_footer(text=f"Nonce: {bot.get_secret_nonce(ctx.author.id)[1]} | Client Seed: {bot.get_secret_nonce(ctx.author.id)[0]}")

    await ctx.send(embed=embed)
    if has_won:
        bot.update_amount(ctx.author.id, (amount * multiplier), type)
    else:
        bot.update_amount(ctx.author.id, -amount, type)


class Rolls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Usage = "The roll commands"

    @commands.command(name="50")
    async def roll_50(self, ctx, type: CoinType, amount: Amount):
        await roll(self.bot, ctx, amount, type, 50, 1.9)

    @commands.command(name="54")
    async def roll_54(self, ctx, type: CoinType, amount: Amount):
        await roll(self.bot, ctx, amount, type, 54, 2)

    @commands.command(name="75")
    async def roll_75(self, ctx, type: CoinType, amount: Amount):
        await roll(self.bot, ctx, amount, type, 75, 3)

    @commands.command(name="95")
    async def roll_95(self, ctx, type: CoinType, amount: Amount):
        await roll(self.bot, ctx, amount, type, 95, 5)

    @roll_50.error
    @roll_54.error
    @roll_75.error
    @roll_95.error
    async def info_error(self, ctx, error):
        embed = Embed(colour=Colour.red())
        embed.set_footer(text="Usage: ![50 | 54 | 75] [rs3 | 07] amount")
        embed.add_field(name='Error', value=error.args[0].replace("Command raised an exception: Exception: ", ""))
        await ctx.send(embed=embed)