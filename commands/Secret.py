import typing

import discord
from discord import Colour
from discord import Embed
from discord.ext import commands

from commands.Amount_converter import Amount
from commands.Coin_converter import CoinType
from economy.Economy import amount_to_string, amount_valid
from economy.Money_type import MoneyType


class Secret(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Usage = "The roll commands"

    @commands.command(name="setseed")
    async def secret_command(self, ctx, secret: typing.Optional[str]):
        if secret is None:
            embed = Embed(colour=Colour.gold(), description=f"Your seed is **{secret}**")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            embed = Embed(colour=Colour.green(), description=f"Successfully changed Seed to **{secret}**")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            self.bot.set_secret(ctx.author.id, secret)

    @secret_command.error
    async def wager_info_error(self, ctx, error):
        await self.info_error(ctx, error, "!secret (user)")

    async def info_error(self, ctx, error, usage):
        embed = Embed(colour=Colour.red())
        embed.set_footer(text=usage)
        embed.add_field(name='Error', value=error.args[0].replace("Command raised an exception: Exception: ", ""))
        await ctx.send(embed=embed)