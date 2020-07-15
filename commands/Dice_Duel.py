import random

from discord import Colour
from discord import Embed
from discord.ext import commands

from commands.Amount_converter import Amount
from commands.Coin_converter import CoinType
from economy.Economy import amount_to_string
from economy.Economy import amount_valid


async def dice_duel(bot, ctx, amount, type):
    message = await bot.checking_database(ctx)
    await amount_valid(bot, ctx.author.id, amount, type, message)
    bot.wagered(ctx.author.id, amount, type)

    user = random.randint(2, 12)
    bot_chance = random.randint(2, 12)

    has_won = user > bot_chance

    if has_won:
        colour = Colour.green()
    elif user == bot_chance:
        colour = Colour.orange()
    else:
        colour = Colour.red()

    embed = Embed(colour=colour, name="Dice duel", description=f"Host: {ctx.author.mention} \nYou Rolled [{user}]")

    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.add_field(name="Range:", value="1-12", inline=False)
    embed.add_field(name="Bot Roll:", value=bot_chance)
    embed.set_thumbnail(url="https://vignette.wikia.nocookie.net/awakenpsrsps/images/f/f2/Dice_bag_detail.png/revision/latest?cb=20151008212452")

    if user == bot_chance:
        embed.add_field(name="Dice Results: ", value="Tie", inline=False)
    else:
        embed.add_field(name="Dice Results: ", value=ctx.author.mention if has_won else bot.user.mention, inline=False)
        embed.add_field(name="Money:", value=f"You won {amount_to_string((amount * 1.9) - amount)}" if has_won else f"You lost {amount_to_string(amount)}", inline=False)

    await message.edit(embed=embed)
    if has_won:
        bot.update_amount(ctx.author.id, (amount * 1.9) - amount, type)
    elif bot_chance != user:
        bot.update_amount(ctx.author.id, -amount, type)


class DD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Usage = "The dice duel commands"

    @commands.command(name="dd")
    async def dd_command(self, ctx, type: CoinType, amount: Amount):
        await dice_duel(self.bot, ctx, amount, type)

    @dd_command.error
    async def info_error(self, ctx, error):
        embed = Embed(colour=Colour.red())
        embed.set_footer(text="Usage: !dd [07 | rs3] amount")
        embed.add_field(name='Error', value=error.args[0].replace("Command raised an exception: Exception: ", ""))
        await ctx.send(embed=embed)
