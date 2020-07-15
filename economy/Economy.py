def amount_to_string(amount):
    if amount >= 1000000000:
        if amount % 1000000000 == 0:
            return "{}b".format(int(amount / 1000000000))
        return "{:.2f}b".format(round(amount / 1000000000, 2))

    if amount >= 1000000:
        if amount % 1000000 == 0:
            return "{}m".format(int(amount / 1000000))
        return "{:.2f}m".format(round(amount / 1000000, 2))

    if amount >= 1000:
        if amount % 1000 == 0:
            return "{}k".format(int(amount / 1000))
        return "{:.2f}k".format(round(amount / 1000, 2))
    else:
        return f"{round(amount, 1)}"


def amount_valid(bot, user_id, amount, type):
    if bot.get_amount(user_id, type) < amount:
        raise Exception(f"Not enough {type.format_string()}")

    if amount < 0:
        raise Exception(f"Can't gamble negative numbers")

    if amount < type.min_amount():
        raise Exception(f"Amount: {amount_to_string(amount)} is below minimum for {type.format_string()}. \n The min amount is {amount_to_string(type.min_amount())}")

    if bot.get_amount(bot.user.id, type) / 2 < amount:
        raise Exception(f"Bot does not have enough money.")
