from discord.ext import commands


def amountToString(amount):
    if amount >= 1000000000:
        return f"{round(amount / 1000000000, 1)}b"
    
    if amount >= 1000000:
        return f"{round(amount / 1000000, 1)}m";
    
    if amount >= 1000:
        return f"{round(amount / 1000, 1)}k";
    else:
        return f"{round(amount, 1)}"
