import typing

from discord import Colour
from discord import Embed
from discord.ext import commands


class Secret(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Usage = "The roll commands"

    @commands.command(name="setseed")
    async def secret_command(self, ctx, secret: typing.Optional[str]):

        embed = Embed(colour=Colour.gold(), description=f"Checking database")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        message = await ctx.send(embed=embed)

        if secret is None:
            embed = Embed(colour=Colour.gold(), description=f"Your seed is **{self.bot.get_secret_nonce(ctx.author.id)[0]}**")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            await message.edit(embed=embed)
        else:
            if self.bot.contains_secret(secret):
                embed = Embed(colour=Colour.red(), description=f"Someone already has that seed")
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                await message.edit(embed=embed)
            elif self.bot.get_secret_nonce(ctx.author.id)[0] == secret:
                embed = Embed(colour=Colour.green(), description=f"You already have that seed")
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                await message.edit(embed=embed)
            else:
                embed = Embed(colour=Colour.green(), description=f"Successfully changed seed to **{secret}**")
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                await message.edit(embed=embed)
                self.bot.set_secret(ctx.author.id, secret)

    @secret_command.error
    async def wager_info_error(self, ctx, error):
        await self.info_error(ctx, error, "!secret (user)")

    async def info_error(self, ctx, error, usage):
        embed = Embed(colour=Colour.red())
        embed.set_footer(text=usage)
        embed.add_field(name='Error', value=error.args[0].replace("Command raised an exception: Exception: ", ""))
        await ctx.send(embed=embed)