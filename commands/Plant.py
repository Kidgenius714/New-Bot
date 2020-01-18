import random

from discord import Colour
from discord import Embed
from discord.ext import commands

from commands.Amount_converter import Amount
from commands.Coin_converter import CoinType
from economy.Economy import amountValid
from economy.Economy import amountToString

flowers = {
    "purple": ["https://cdn.discordapp.com/attachments/628820715013013546/629639422316380160/purple.png", Colour.magenta(), "cold"],
    "blue": ["https://cdn.discordapp.com/attachments/628820715013013546/629639401768484864/blue.png", Colour.blue(), "cold"],
    "pastel": ["https://cdn.discordapp.com/attachments/628820715013013546/629639424195428352/pastel.png", Colour.green(), "cold"],
    "yellow": ["https://cdn.discordapp.com/attachments/628820715013013546/629639427508928543/yelow.png", Colour.from_rgb(255, 255, 0), "hot"],
    "red": ["https://images-ext-1.discordapp.net/external/jtOX9o1yvoetSwsOiZ8G4cUlnU3LzcE_8gnNPN32fHY/"
            "https/cdn.discordapp.com/emojis/567247590102663180.png", Colour.red(), "hot"],
    "orange": ["https://cdn.discordapp.com/attachments/628820715013013546/629639412376010752/Orange.png", Colour.orange(), "hot"],
    "rainbow": ["https://cdn.discordapp.com/attachments/628820715013013546/629639426653421569/rainbow.png", Colour.from_rgb(0, 255, 255), "Host Wins"]
   }


class Plant(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Usage = "The roll commands"

    @commands.command(name="plant")
    async def plant_command(self, ctx, hot, type: CoinType, amount: Amount):
        amountValid(self.bot, ctx.author.id, amount, type)
        self.bot.wagered(ctx.author.id, amount, coin_type)
        if hot.lower() != "hot" and hot.lower() != "cold":
            raise Exception("You must choose hot or cold")

        flower_names = [*flowers]

        flower = flower_names[random.randint(0, len(flower_names) - 1)]
        has_won = flowers[flower][2].lower() == hot.lower()

        embed = Embed(title="Picking Flowers!", colour=flowers[flower][1])
        embed.set_thumbnail(url=flowers[flower][0])
        embed.add_field(name=f"A {flower.title()} has been drawn!",
                        value=f"Host by: {ctx.author.mention}\n\n\n You **{'won' if has_won else 'lost'}** {amountToString(amount)}!")
        await ctx.send(embed=embed)
        if has_won:
            self.bot.update_amount(ctx.author.id, amount, type)
        else:
            self.bot.update_amount(ctx.author.id, -amount, type)

    @plant_command.error
    async def info_error(self, ctx, error):
        embed = Embed(colour=Colour.red())
        embed.set_footer(text="Usage: !plant [hot|cold] type amount")
        embed.add_field(name='Error', value=error.args[0].replace("Command raised an exception: Exception: ", ""))
        await ctx.send(embed=embed)
