from discord.ext import commands
from economy.Money_type import MoneyType


class CoinType(commands.Converter):
    async def convert(self, ctx, argument):
        if argument.lower() == "rs3":
            return MoneyType.RS3
        elif argument.lower() == "07":
            return MoneyType.R07
        elif argument.lower() == "token":
            return MoneyType.TOKENS
        else:
            raise commands.BadArgument(f"{argument} is not a rs3, 07 or tokens")
