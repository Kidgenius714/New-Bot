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

class BlackJack(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.Usage = "The blackjack commands"
        self.card_names = self.bot.config['card_names']
        self.hidden_card = self.bot.config["hidden_card"]

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
        data[author_id]["author_cards"] = [self.draw_card(author_id, False), self.draw_card(author_id, False)]
        data[author_id]["bot_cards"] = [self.draw_card(author_id, True)]

        self.bot.update_amount(author_id, -amount, coin_type)
        await self.print_embed(author_id, True)

    def calculate_total(self, cards):
        total = 0
        for card in cards:
            total += card["value"]
        return total

    async def embed_cards(self, deck, hidden_card):
        if hidden_card:
            cards = "".join(map(lambda card: card["emoji"], deck)) + self.hidden_card
        else:
            cards = "".join(map(lambda card: card["emoji"], deck))
        total = " + ".join(map(lambda card: str(card["value"]), deck)) + f" = {self.calculate_total(deck)}"
        return f"{cards}\n{total}"

    def get_winner_at_moment(self, id):
        author_total = self.calculate_total(data[id]["author_cards"])
        bot_total = self.calculate_total(data[id]["bot_cards"])

        if bot_total > 21 and author_total > 21:
            return Winner.TIE

        if author_total > 21:
            return Winner.BOT

        if bot_total > 21:
            return Winner.AUTHOR

        if bot_total == author_total:
            return Winner.TIE

        return Winner.BOT if bot_total > author_total else Winner.AUTHOR

    async def bust(self, id):

        embed = Embed(colour=Colour.red())

        player_deck = data[id]["author_cards"]
        embed.add_field(name="Player", value=await self.embed_cards(player_deck, False))

        bot_deck = data[id]["bot_cards"]
        embed.add_field(name="Bot", value=await self.embed_cards(bot_deck, False))

        embed.set_footer(
            text=f"Bust I win! Better luck next time. Amount Lost: {amount_to_string(data[id]['amount'])} {data[id]['type'].format_string()}",
            icon_url=data[id]["icon_url"])

        if data[id]["msg_id"] is None:
            data[id]["msg_id"] = await data[id]["channel"].send(embed=embed)
        else:
            await data[id]["msg_id"].edit(embed=embed)

    async def win(self, id, bot):

        embed = Embed(colour=Colour.green())

        player_deck = data[id]["author_cards"]
        embed.add_field(name="Player", value=await self.embed_cards(player_deck, False))

        bot_deck = data[id]["bot_cards"]
        embed.add_field(name="Bot", value=await self.embed_cards(bot_deck, False))

        embed.set_footer(
            text=f"I guess you win this time. Amount Won: {amount_to_string(data[id]['amount'])} {data[id]['type'].format_string()}",
            icon_url=data[id]["icon_url"])

        if data[id]["msg_id"] is None:
            data[id]["msg_id"] = await data[id]["channel"].send(embed=embed)
        else:
            await data[id]["msg_id"].edit(embed=embed)

        bot.update_amount(id, (data[id]['amount'] * 1.9), data[id]['type'])

    async def tie(self, id, bot):

        embed = Embed(colour=Colour.gold())

        player_deck = data[id]["author_cards"]
        embed.add_field(name="Player", value=await self.embed_cards(player_deck, False))

        bot_deck = data[id]["bot_cards"]
        embed.add_field(name="Bot", value=await self.embed_cards(bot_deck, False))

        embed.set_footer(text=f"It ended in a tie. No amount lost or given.", icon_url=data[id]["icon_url"])

        if data[id]["msg_id"] is None:
            data[id]["msg_id"] = await data[id]["channel"].send(embed=embed)
        else:
            await data[id]["msg_id"].edit(embed=embed)

        bot.update_amount(id, (data[id]['amount']), data[id]['type'])

    async def hit(self, id, channel, bot):
        if data[id]["author_stand"]:
            embed = Embed(colour=Colour.red())
            embed.set_footer(text=usage, icon_url=data[id]["icon_url"])
            embed.add_field(name='Error', value="You cannot hit after standing!")
            await channel.send(embed=embed)

        data[id]["author_cards"].append(self.draw_card(id, False))

        if self.calculate_total(data[id]["author_cards"]) > 21:
            await self.finish(id, Winner.BOT, bot)
        else:
            await self.print_embed(id, False)

    async def bot_turn(self, id, bot):
        data[id]["bot_cards"].append(self.draw_card(id, True))
        if self.calculate_total(data[id]["bot_cards"]) < 17:
            await self.print_embed(id, False)
            await self.bot_turn(id, bot)
        else:
            await self.finish(id, self.get_winner_at_moment(id), bot)

    async def stand(self, id, bot):
        data[id]["author_stand"] = True
        await self.bot_turn(id, bot)

    def draw_card(self, id, bot):
        card = data[id]["deck"].pop()
        if card["value"] == -1:
            deck = data[id]["bot_cards" if bot else "author_cards"]
            if self.calculate_total(deck) > 10:
                card["value"] = 1
            else:
                card["value"] = 11
        return card

    async def finish(self, id, winner: Winner, bot):
        if winner == Winner.BOT:
            await self.bust(id)

        if winner == Winner.AUTHOR:
            await self.win(id, bot)

        if winner == Winner.TIE:
            await self.tie(id, bot)

        data.pop(id)


    async def print_embed(self, id, hidden_card):
        embed = Embed()

        player_deck = data[id]["author_cards"]
        embed.add_field(name="Player", value=await self.embed_cards(player_deck, False))

        bot_deck = data[id]["bot_cards"]
        embed.add_field(name="Bot", value=f"{await self.embed_cards(bot_deck, hidden_card)}")

        if data[id]["msg_id"] is None:
            data[id]["msg_id"] = await data[id]["channel"].send(embed=embed)
        else:
            await data[id]["msg_id"].edit(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower().startswith("hit"):
            if message.author.id in data:
                await message.delete()
                await self.hit(message.author.id, message.channel, self.bot)
                return

            embed = Embed(colour=Colour.red())
            embed.set_footer(text=usage)
            embed.add_field(name='Error', value="You are not in a game!")
            await message.channel.send(embed=embed)

        if message.content.lower().startswith("stand"):
            if message.author.id in data:
                await message.delete()
                await self.stand(message.author.id, self.bot)
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
