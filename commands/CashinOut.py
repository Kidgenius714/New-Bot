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


def is_host():
    async def predicate(ctx):
        if ctx.guild.get_role(config.cashier_role_id).position <= ctx.author.top_role.position:
            return True
        else:
            raise commands.MissingRole(ctx.guild.get_role(config.cashier_role_id).name)
    return commands.check(predicate)

request_id = config.request_channel_id
cashiers_id = config.cashier_channel_id
cashier_role_id = config.cashier_role_id

ids = {
}

class Cash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Usage = "The roll commands"

    @commands.command(name="cashin")
    async def cashin(self, ctx, types: CoinType, amounts: Amount):
        id = len(ids)
        embed = Embed()
        embed.add_field(name="Request Host", value=f"{ctx.author.mention}, You are requesting to cashin {amountToString(amounts)} {types.format_string()}. A cashier will be assigned to you, ID: {id}", inline=False)
        await ctx.guild.get_channel(request_id).send(embed=embed)

        await ctx.guild.get_channel(cashiers_id).send(f"{ctx.guild.get_role(cashier_role_id).mention}, {ctx.author.mention} wants to insert **{amountToString(amounts)}** {types.format_string()}. Use !accept {id}")

        ids[id] = {
            user: ctx.author,
            amount: amounts,
            type: types
        }

        print(ids)

    @commands.command(name="cashout")
    async def cashout(self, ctx, types: CoinType, amounts: Amount):
        id = len(ids)
        embed = Embed()
        embed.add_field(name="Request Host", value=f"{ctx.author.mention}, You are requesting to cashout {amountToString(amounts)} {types.format_string()}. A cashier will be assigned to you, ID: {id}", inline=False)
        await ctx.guild.get_channel(request_id).send(embed=embed)

        await ctx.guild.get_channel(cashiers_id).send(f"{ctx.guild.get_role(cashier_role_id).mention}, {ctx.author.mention} wants to withdraw **{amountToString(amounts)}** {types.format_string()}. Use !accept {id}")

        ids[id] = {
            "user": ctx.author,
            "amount": amounts,
            "type": types
        }

    @is_host()
    @commands.command(name="accept")
    async def accept(self, ctx, id: int):
        if not(id in ids):
            await ctx.send("There is no matching id or the id is expired!")

        info = ids[id]

        embed = Embed(colour=Colour.green())
        embed.add_field(name='Cashier found!', value=f"{ctx.author.mention} is going to be your cashier {info["user"].mention}, amount {amountToString(info["amount"])} {info["type"].format_string()}. ID: {id}")
        await ctx.send(embed=embed)
        ids.pop(id)


    @cashin.error
    async def cashin_info_error(self, ctx, error):
        await self.info_error(ctx, error, "!cashin [rs3 | 07] amount")

    @cashout.error
    async def cashout_info_error(self, ctx, error):
        await self.info_error(ctx, error, "!cashout [rs3 | 07] amount")

    @accept.error
    async def accept_info_error(self, ctx, error):
        await self.info_error(ctx, error, "!cashout id")

    async def info_error(self, ctx, error, usage):
        embed = Embed(colour=Colour.red())
        embed.set_footer(text=usage)
        embed.add_field(name='Error', value=error.args[0].replace("Command raised an exception: Exception: ", ""))
        await ctx.send(embed=embed)