import typing

import discord
from discord import Colour
from discord import Embed
from discord.ext import commands

from commands.Amount_converter import Amount
from commands.Coin_converter import CoinType
from economy.Economy import amount_to_string, amount_valid
from economy.Money_type import MoneyType


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Usage = "The roll commands"


    def can_modify_economy(self, ctx):
        if ctx.guild.get_role(self.bot.config['can_modify_economy']).position <= ctx.author.top_role.position:
            return True
        else:
            raise commands.MissingRole(ctx.guild.get_role(self.bot.config['can_modify_economy']).name)

    @commands.command(name="wallet", aliases=["w"])
    async def wallet(self, ctx, user: typing.Optional[discord.Member]):
        message = await self.bot.checking_database(ctx)
        if user is None:
            user = ctx.author
        embed = Embed(colour=Colour.gold())
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.add_field(name="RS3 Balance",
                        value=amount_to_string(self.bot.get_amount(user.id, MoneyType.RS3)), inline=False)
        embed.add_field(name="07 Balance",
                        value=amount_to_string(self.bot.get_amount(user.id, MoneyType.R07)), inline=False)
        await message.edit(embed=embed)

    @commands.command(name="wager")
    async def wager(self, ctx, user: typing.Optional[discord.Member]):
        message = await self.bot.checking_database(ctx)
        if user is None:
            user = ctx.author
        embed = Embed(colour=Colour.gold())
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.add_field(name="RS3 Wager",
                        value=amount_to_string(self.bot.get_amount(user.id, MoneyType.WagRS3)), inline=False)
        embed.add_field(name="07 Wager",
                        value=amount_to_string(self.bot.get_amount(user.id, MoneyType.WagR07)), inline=False)
        await message.edit(embed=embed)

    @commands.command(name="set")
    async def set_wallet(self, ctx, coin_type: CoinType, user: discord.Member, amount: Amount):
        if not self.can_modify_economy(ctx):
            return

        embed = Embed(colour=Colour.gold())
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Set Request", value=f"Successfully set {coin_type.format_string()} to {amount_to_string(amount)} for {user.mention} wallet", inline=False)
        await ctx.send(embed=embed)
        self.bot.set_amount(user.id, amount, coin_type)

    @commands.command(name="update")
    async def update_wallet(self, ctx, coin_type: CoinType, user: discord.Member, amount: Amount):
        if not self.can_modify_economy(ctx):
            return
        embed = Embed(colour=Colour.gold())
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Update Request", value=f"Successfully updated {amount_to_string(amount)} {coin_type.format_string()} to {user.mention} wallet", inline=False)
        await ctx.send(embed=embed)
        self.bot.update_amount(user.id, amount, coin_type)

    @commands.command(name="transfer")
    async def transfer(self, ctx, coin_type: CoinType, user: discord.Member, amount: Amount):
        message = await self.bot.checking_database(ctx)
        await amount_valid(self.bot, ctx.author.id, amount, coin_type, message)
        embed = Embed(colour=Colour.gold())
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Transfer Request", value=f"Successfully transferred {amount_to_string(amount)} {coin_type.format_string()} to {user.mention} wallet", inline=False)
        await message.edit(embed=embed)
        self.bot.update_amount(user.id, amount, coin_type)
        self.bot.update_amount(ctx.author.id,0 -amount, coin_type)

    @wallet.error
    async def wallet_info_error(self, ctx, error):
        await self.info_error(ctx, error, "![w | wallet] user")

    @wager.error
    async def wager_info_error(self, ctx, error):
        await self.info_error(ctx, error, "!wager user")

    @set_wallet.error
    async def set_info_error(self, ctx, error):
        await self.info_error(ctx, error, "!set [rs3 | 07] user amount")

    @update_wallet.error
    async def update_info_error(self, ctx, error):
        await self.info_error(ctx, error, "!update [rs3 | 07] user amount")

    @transfer.error
    async def transfer_info_error(self, ctx, error):
        await self.info_error(ctx, error, "!transfer [rs3 | 07] user amount")

    async def info_error(self, ctx, error, usage):
        embed = Embed(colour=Colour.red())
        embed.set_footer(text=usage)
        embed.add_field(name='Error', value=error.args[0].replace("Command raised an exception: Exception: ", ""))
        await ctx.send(embed=embed)