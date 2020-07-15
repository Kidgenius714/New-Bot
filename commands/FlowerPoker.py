import random

from discord import Colour, Embed
from discord.ext import commands
from enum import Enum

from commands.Amount_converter import Amount
from commands.Coin_converter import CoinType
from economy.Economy import amount_valid
from economy.Economy import amount_to_string


class Hands(Enum):
    BUST = 1
    PAIR_1 = 2
    PAIR_2 = 3
    AK30 = 4
    FULL_HOUSE = 5
    AK40 = 6
    AK50 = 7

    def format_string(self):
        if self == Hands.PAIR_1:
            return "1 Pair"
        if self == Hands.PAIR_2:
            return "2 Pairs"
        if self == Hands.AK30:
            return "30ak"
        if self == Hands.AK40:
            return "40ak"
        if self == Hands.AK50:
            return "50ak"
        return self.name.replace("_", " ").title()


def analyse(arr):
    count = []

    for i in set(arr):
        count.append(arr.count(i))

    if 5 in count:
        return Hands.AK50
    elif 4 in count:
        return Hands.AK40
    elif 2 in count and 3 in count:
        return Hands.FULL_HOUSE
    elif 3 in count:
        return Hands.AK30
    elif count.count(2) == 2:
        return Hands.PAIR_2
    elif 2 in count:
        return Hands.PAIR_1
    else:
        return Hands.BUST


if __name__ == "__main__":
    arr = ["hey343", "hey13", "hey13", "hey332", "hey3"]
    arr2 = ["hey343", "hey13", "hey13", "hey332", "hey332"]
    print(analyse(arr).format_string())
    print(analyse(arr2).format_string())
    print(analyse(arr).value > analyse(arr2).value)


class FlowerPoker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Usage = "The Flower poker commands"
        self.flowers = self.bot.config['flowers']

    def get_flower(self):
        return self.flowers[random.randint(0, len(self.flowers) - 1)]

    @commands.command(name="fp")
    async def flower_poker(self, ctx, type: CoinType, amount: Amount):
        message = await self.bot.checking_database(ctx)
        global embed
        await amount_valid(self.bot, ctx.author.id, amount, type, message)
        self.bot.wagered(ctx.author.id, amount, type)

        player_flowers = [self.get_flower(), self.get_flower(), self.get_flower(), self.get_flower(), self.get_flower()]
        bot_flowers = [self.get_flower(), self.get_flower(), self.get_flower(), self.get_flower(), self.get_flower()]

        result_player = analyse(player_flowers)
        result_bot = analyse(bot_flowers)

        if result_player.value > result_bot.value:
            embed = Embed(colour=Colour.green(), description=f"You won **{amount_to_string(amount)} {type.format_string()}**")

        if result_player.value < result_bot.value:
            embed = Embed(colour=Colour.red(), description=f"You lost **{amount_to_string(amount)} {type.format_string()}**")

        if result_player.value == result_bot.value:
            embed = Embed(colour=Colour.dark_grey(), description=f"You were refunded")

        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name=f"Bot's Hand ({result_bot.format_string()})",
                        value=" ".join(bot_flowers), inline=False)
        embed.add_field(name=f"Players's Hand ({result_player.format_string()})",
                        value=" ".join(player_flowers), inline=False)

        await message.edit(embed=embed)

        if result_player.value > result_bot.value:
            self.bot.update_amount(ctx.author.id, (amount), type)
        if result_player.value < result_bot.value:
            self.bot.update_amount(ctx.author.id, -amount, type)

    @flower_poker.error
    async def info_error(self, ctx, error):
        embed = Embed(colour=Colour.red())
        embed.set_footer(text="Usage: !flower [rs3 | 07] amount")
        embed.add_field(name='Error', value=error.args[0].replace("Command raised an exception: Exception: ", ""))
        await ctx.send(embed=embed)
        raise error