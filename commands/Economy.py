import typing

import discord
from discord import Colour
from discord import Embed
from discord.ext import commands

import config
from commands.Amount_converter import Amount
from commands.Coin_converter import CoinType
from economy.Economy import amountToString
from economy.Money_type import MoneyType


def can_modify_economy():
    async def predicate(ctx):
        if ctx.guild.get_role(config.can_modify_economy).position <= ctx.author.top_role.position:
            return True
        else:
            raise commands.MissingRole(ctx.guild.get_role(config.can_modify_economy).name)
    return commands.check(predicate)


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Usage = "The roll commands"

    @commands.command(name="wallet", aliases=["w"])
    async def wallet(self, ctx, user: typing.Optional[discord.Member]):
        if user is None:
            user = ctx.author
        # if user == self.bot.user:
        #     raise Exception("You are unable to see the bot's wallet!")
        embed = Embed(colour=Colour.gold())
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.add_field(name="RS3 Balance",
                        value=amountToString(self.bot.get_amount(user.id, MoneyType.RS3)), inline=False)
        embed.add_field(name="07 Balance",
                        value=amountToString(self.bot.get_amount(user.id, MoneyType.R07)), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="wager")
    async def wallet(self, ctx, user: typing.Optional[discord.Member]):
        if user is None:
            user = ctx.author
        # if user == self.bot.user:
        #     raise Exception("You are unable to see the bot's wallet!")
        embed = Embed(colour=Colour.gold())
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.add_field(name="RS3 Wager",
                        value=amountToString(self.bot.get_amount(user.id, MoneyType.WagRS3)), inline=False)
        embed.add_field(name="07 Wager",
                        value=amountToString(self.bot.get_amount(user.id, MoneyType.WagR07)), inline=False)
        await ctx.send(embed=embed)

    @can_modify_economy()
    @commands.command(name="set")
    async def set_wallet(self, ctx, type: CoinType, user: discord.Member, amount: Amount):
        embed = Embed(colour=Colour.gold())
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Set Request", value=f"Successfully set {type.format_string()} to {amountToString(amount)} for {user.mention} wallet", inline=False)
        await ctx.send(embed=embed)
        self.bot.set_amount(user.id, amount, type)

    @can_modify_economy()
    @commands.command(name="update")
    async def update(self, ctx, type: CoinType, user: discord.Member, amount: Amount):
        embed = Embed(colour=Colour.gold())
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Update Request", value=f"Successfully updated {amountToString(amount)} {type.format_string()} to {user.mention} wallet", inline=False)
        await ctx.send(embed=embed)
        self.bot.update_amount(user.id, amount, type)

    @wallet.error
    async def wallet_info_error(self, ctx, error):
        await self.info_error(ctx, error, "![w | wallet] user")

    @set_wallet.error
    async def wallet_info_error(self, ctx, error):
        await self.info_error(ctx, error, "!set [rs3 | 07] user amount")

    @update.error
    async def wallet_info_error(self, ctx, error):
        await self.info_error(ctx, error, "!update [rs3 | 07] user amount")

    async def info_error(self, ctx, error, usage):
        embed = Embed(colour=Colour.red())
        embed.set_footer(text=usage)
        embed.add_field(name='Error', value=error.args[0].replace("Command raised an exception: Exception: ", ""))
        await ctx.send(embed=embed)