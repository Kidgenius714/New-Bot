import random

from discord import Colour
from discord import Embed
from discord.ext import commands

from economy.Economy import amount_to_string
from economy.Economy import amount_valid
from economy.Money_type import MoneyType

items = [
    ["Dragon Helberd", 149300, "https://cdn.discordapp.com/attachments/650248256915243018/726472130161541160/Dragon_halberd.gif"],
    ["Dragon sq Shield", 299800, "https://cdn.discordapp.com/attachments/650248256915243018/726472150952706128/Dragon_sq_Shield.gif"],
    ["Dragon battleaxe", 119200, "https://cdn.discordapp.com/attachments/650248256915243018/726472117050409041/Dragon_battleaxe.gif"],
    ["Dragon Boots", 349600, "https://cdn.discordapp.com/attachments/650248256915243018/726472119545757717/Dragon_boots.gif"],
    ["Dragon harpoon", 465800, "https://cdn.discordapp.com/attachments/650248256915243018/726472112667230298/Dragon_2h.gif"],
    ["Dragon limbs", 2600000, "https://cdn.discordapp.com/attachments/650248256915243018/726472134104449034/Dragon_limbs.gif"],
    ["Dragon platebody", 3400000, "https://cdn.discordapp.com/attachments/650248256915243018/726472146834030622/Dragon_platebody.gif"],
    ["Dragon pickaxe", 5300000, "https://cdn.discordapp.com/attachments/650248256915243018/726472142039941120/Dragon_pickaxe.gif"],
    ["Lava Dragon mask", 1300000, "https://cdn.discordapp.com/attachments/650248256915243018/726472155302330389/Lava_dragon_mask.gif"],
    ["Dragon crossbow (u)", 2900000, "https://cdn.discordapp.com/attachments/650248256915243018/726472123153121421/Dragon_crossbow_u.gif"],
    ["Dragon metal lump", 1200000, "https://cdn.discordapp.com/attachments/650248256915243018/726472137694773328/Dragon_metal_lump.gif"]
]

rare_items = [
    ["Primordial boots", 32100000, "https://cdn.discordapp.com/attachments/650248256915243018/726472158590795796/Primordial_boots.gif"]
]


class Chest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Usage = "The dice duel commands"

    @commands.command(name="chest")
    async def chest_command(self, ctx):
        amount_valid(self.bot, ctx.author.id, 3000000, MoneyType.R07)


        if random.randint(0, 100) == 0:

            i = random.randint(0, len(rare_items) - 1)

            embed = Embed(colour=Colour.blurple(), description=f"You found a **{rare_items[i][0]}** it is worth **{amount_to_string(rare_items[i][1])} 07**")

            embed.set_thumbnail(url=rare_items[i][2])

            self.bot.update_amount(ctx.author.id, rare_items[i][1] - 3000000, MoneyType.R07)

            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

        else:

            i = random.randint(0, len(items) - 1)

            embed = Embed(colour=Colour.blurple(),
                          description=f"You found a **{items[i][0]}** it is worth **{amount_to_string(items[i][1])} 07**")

            embed.set_image(url=items[i][2])

            self.bot.update_amount(ctx.author.id, items[i][1] - 3000000, MoneyType.R07)

            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @chest_command.error
    async def info_error(self, ctx, error):
        embed = Embed(colour=Colour.red())
        embed.set_footer(text="Usage: !chest")
        embed.add_field(name='Error', value=error.args[0].replace("Command raised an exception: Exception: ", ""))
        await ctx.send(embed=embed)
