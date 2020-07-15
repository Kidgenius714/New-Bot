import random
from enum import Enum

from discord import Colour
from discord import Embed
from discord.ext import commands

from commands.Amount_converter import Amount
from commands.Coin_converter import CoinType
from economy.Economy import amount_to_string
from economy.Economy import amount_valid

data = {}

usage = "Usage: !bj type amount"

class Winner(Enum):
    AUTHOR = 0
    BOT = 1
    TIE = 2


def calculate_total(cards):
    total = 0
    for card in cards:
        total += card["value"]
    return total


async def embed_cards(deck):
    cards = "".join(map(lambda card: card["emoji"], deck))
    total = " + ".join(map(lambda card: str(card["value"]), deck)) + f" = {calculate_total(deck)}"
    return f"{cards}\n{total}"


async def print_embed(id):
    embed = Embed()

    player_deck = data[id]["author_cards"]
    embed.add_field(name="Player", value=await embed_cards(player_deck))

    bot_deck = data[id]["bot_cards"]
    embed.add_field(name="Bot", value=await embed_cards(bot_deck))

    if data[id]["msg_id"] is None:
        data[id]["msg_id"] = await data[id]["channel"].send(embed=embed)
    else:
        await data[id]["msg_id"].edit(embed=embed)


def get_winner_at_moment(id):
    author_total = calculate_total(data[id]["author_cards"])
    bot_total = calculate_total(data[id]["bot_cards"])

    if bot_total > 21 and author_total > 21:
        return Winner.TIE

    if author_total > 21:
        return Winner.BOT

    if bot_total > 21:
        return Winner.AUTHOR

    if bot_total == author_total:
        return Winner.TIE

    return Winner.BOT if bot_total > author_total else Winner.AUTHOR


async def bust(id):

    embed = Embed(colour=Colour.red())

    player_deck = data[id]["author_cards"]
    embed.add_field(name="Player", value=await embed_cards(player_deck))

    bot_deck = data[id]["bot_cards"]
    embed.add_field(name="Bot", value=await embed_cards(bot_deck))

    embed.set_footer(text=f"Bust I win! Better luck next time. Amount Lost: {amount_to_string(data[id]['amount'])} {data[id]['type'].format_string()}", icon_url=data[id]["icon_url"])

    if data[id]["msg_id"] is None:
        data[id]["msg_id"] = await data[id]["channel"].send(embed=embed)
    else:
        await data[id]["msg_id"].edit(embed=embed)


async def win(id, bot):

    embed = Embed(colour=Colour.green())

    player_deck = data[id]["author_cards"]
    embed.add_field(name="Player", value=await embed_cards(player_deck))

    bot_deck = data[id]["bot_cards"]
    embed.add_field(name="Bot", value=await embed_cards(bot_deck))

    embed.set_footer(text=f"I guess you win this time. Amount Won: {amount_to_string(data[id]['amount'])} {data[id]['type'].format_string()}", icon_url=data[id]["icon_url"])

    if data[id]["msg_id"] is None:
        data[id]["msg_id"] = await data[id]["channel"].send(embed=embed)
    else:
        await data[id]["msg_id"].edit(embed=embed)

    bot.update_amount(id, (data[id]['amount'] * 1.9), data[id]['type'])


async def tie(id, bot):

    embed = Embed(colour=Colour.gold())

    player_deck = data[id]["author_cards"]
    embed.add_field(name="Player", value=await embed_cards(player_deck))

    bot_deck = data[id]["bot_cards"]
    embed.add_field(name="Bot", value=await embed_cards(bot_deck))

    embed.set_footer(text=f"It ended in a tie. No amount lost or given.", icon_url=data[id]["icon_url"])

    if data[id]["msg_id"] is None:
        data[id]["msg_id"] = await data[id]["channel"].send(embed=embed)
    else:
        await data[id]["msg_id"].edit(embed=embed)

    bot.update_amount(id, (data[id]['amount']), data[id]['type'])


async def hit(id, channel, bot):
    if data[id]["author_stand"]:
        embed = Embed(colour=Colour.red())
        embed.set_footer(text=usage, icon_url=data[id]["icon_url"])
        embed.add_field(name='Error', value="You cannot hit after standing!")
        await channel.send(embed=embed)

    data[id]["author_cards"].append(draw_card(id, False))

    if calculate_total(data[id]["author_cards"]) > 21:
        await finish(id, Winner.BOT, bot)
    else:
        await print_embed(id)


async def bot_turn(id, bot):
    data[id]["bot_cards"].append(draw_card(id, True))
    if calculate_total(data[id]["bot_cards"]) < 17:
        await print_embed(id)
        await bot_turn(id, bot)
    else:
        await finish(id, get_winner_at_moment(id), bot)


async def stand(id, bot):
    data[id]["author_stand"] = True
    await bot_turn(id, bot)


def draw_card(id, bot):
    card = data[id]["deck"].pop()
    if card["value"] == -1:
        deck = data[id]["bot_cards" if bot else "author_cards"]
        if calculate_total(deck) > 10:
            card["value"] = 1
        else:
            card["value"] = 11
    return card


async def finish(id, winner: Winner, bot):
    if winner == Winner.BOT:
        await bust(id)

    if winner == Winner.AUTHOR:
        await win(id, bot)

    if winner == Winner.TIE:
        await tie(id, bot)

    data.pop(id)


class BlackJack(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.Usage = "The blackjack commands"
        self.card_names = self.bot.config['card_names']

    @commands.command(name="bj")
    async def bj_command(self, ctx, coin_type: CoinType, amount: Amount):
        message = await self.bot.checking_database(ctx)
        await amount_valid(self.bot, ctx.author.id, amount, coin_type, message)
        self.bot.wagered(ctx.author.id, amount, coin_type)
        author_id = ctx.author.id

        if author_id in data:
            raise Exception("You are already in a blackjack game, please use hit or stand")

        data[author_id] = {
            "channel": ctx.channel,
            "msg_id": message,
            "author_cards": [],
            "bot_cards": [],
            "deck": self.card_names * 16,
            "author_stand": False,
            "type": coin_type,
            "amount": amount,
            "icon_url": ctx.author.avatar_url
        }
        random.shuffle(data[author_id]["deck"])
        data[author_id]["author_cards"] = [draw_card(author_id, False), draw_card(author_id, False)]

        self.bot.update_amount(author_id, -amount, coin_type)
        await print_embed(author_id)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower().startswith("hit"):
            if message.author.id in data:
                await message.delete()
                await hit(message.author.id, message.channel, self.bot)
                return

            embed = Embed(colour=Colour.red())
            embed.set_footer(text=usage)
            embed.add_field(name='Error', value="You are not in a game!")
            await message.channel.send(embed=embed)

        if message.content.lower().startswith("stand"):
            if message.author.id in data:
                await message.delete()
                await stand(message.author.id, self.bot)
                return
            embed = Embed(colour=Colour.red())
            embed.set_footer(text=usage)
            embed.add_field(name='Error', value="You are not in a game!")
            await message.send(embed=embed)

    @bj_command.error
    async def info_error(self, ctx, error):
        embed = Embed(colour=Colour.red())
        embed.set_footer(text=usage)
        embed.add_field(name='Error', value=error.args[0].replace("Command raised an exception: Exception: ", ""))
        await ctx.send(embed=embed)
        raise error
