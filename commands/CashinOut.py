from discord import Colour
from discord import Embed
from discord.ext import commands

from commands.Amount_converter import Amount
from commands.Coin_converter import CoinType
from economy.Economy import amount_to_string
from economy.Economy import amount_valid


def is_host():
    async def predicate(self, ctx):
        if ctx.guild.get_role(self.bot.config['cashier_role_id']).position <= ctx.author.top_role.position:
            return True
        else:
            raise commands.MissingRole(ctx.guild.get_role(self.bot.config['cashier_role_id']).name)

    return commands.check(predicate)



ids = {
}

class Cash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Usage = "The roll commands"

    @commands.command(name="cashin")
    async def cashin(self, ctx, types: CoinType, amounts: Amount):
        message = await self.bot.checking_database(ctx)
        await amount_valid(self.bot, ctx.author.id, amounts, types, message)
        await message.delete()
        cashin_id = len(ids)
        embed = Embed()
        embed.add_field(name="Request Host", value=f"{ctx.author.mention}, You are requesting to cashin {amount_to_string(amounts)} {types.format_string()}. A cashier will be assigned to you, ID: {cashin_id}", inline=False)
        await ctx.guild.get_channel(self.bot.config['request_channel_id']).send(embed=embed)

        await ctx.guild.get_channel(self.bot.config["cashier_channel_id"]).send(
            f"{ctx.guild.get_role(self.bot.config['cashier_role_id']).mention}, {ctx.author.mention} wants to insert **{amount_to_string(amounts)}** {types.format_string()}. Use !accept {cashin_id}")

        ids[cashin_id] = {
            "user": ctx.author,
            "amount": amounts,
            "type": types
        }

    @commands.command(name="cashout")
    async def cashout(self, ctx, types: CoinType, amounts: Amount):
        message = await self.bot.checking_database(ctx)
        await amount_valid(self.bot, ctx.author.id, amounts, types, message)
        await message.delete()
        cashout_id = len(ids)
        embed = Embed()
        embed.add_field(name="Request Host",
                        value=f"{ctx.author.mention}, You are requesting to cashout {amount_to_string(amounts)} {types.format_string()}. A cashier will be assigned to you, ID: {cashout_id}", inline=False)

        if ctx.guild.get_channel(self.bot.config["request_channel_id"]) is None:
            raise LookupError("Cannot find channel with id " + self.bot.config["request_channel_id"])

        if ctx.guild.get_channel(self.bot.config["cashier_channel_id"]) is None:
            raise LookupError("Cannot find channel with id " + self.bot.config["cashier_channel_id"])

        await ctx.guild.get_channel(self.bot.config['request_channel_id']).send(embed=embed)

        await ctx.guild.get_channel(self.bot.config["cashier_channel_id"]).send(f"{ctx.guild.get_role(self.bot.config['cashier_role_id']).mention}, {ctx.author.mention} wants to withdraw **{amount_to_string(amounts)}** {types.format_string()}. Use !accept {cashout_id}")

        ids[cashout_id] = {
            "user": ctx.author,
            "amount": amounts,
            "type": types
        }

    @is_host()
    @commands.command(name="accept")
    async def accept(self, ctx, accept_id: int):
        if not (accept_id in ids):
            await ctx.send("There is no matching id or the id is expired!")

        info = ids[accept_id]

        embed = Embed(colour=Colour.green())
        embed.add_field(name='Cashier found!', value=f"{ctx.author.mention} is going to be your cashier {info['user'].mention}, amount {amount_to_string(info['amount'])} {info['type'].format_string()}. ID: {accept_id}")
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