from discord.ext import commands


class CMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Usage = "The CMD commands"

    @commands.command(name="cmd")
    async def cmd_command(self, ctx):
        ctx.user