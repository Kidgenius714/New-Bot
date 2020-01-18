import pymongo
from discord.ext import commands

import config
from commands.DD import DD
from commands.Plant import Plant
from commands.Economy import Economy
from commands.Blackjack import BlackJack
from commands.Rolls import Rolls
from economy.Money_type import MoneyType
from commands.CashinOut import Cash

client = commands.Bot(command_prefix=config.prefix, case_insensitive=True);

mongo_client = pymongo.MongoClient(config.mongo_url)
coins = mongo_client[config.mongo_database][config.mongo_collection]

cache = {}


def update_amount(user, amount, type):
    previous_amount = get_amount(user, type)
    set_amount(user, previous_amount + amount, type)

    if user == client.user.id:
        return;

    previous_amount_bot = get_amount(client.user.id, type)
    set_amount(client.user.id, previous_amount_bot - amount, type)

    if previous_amount_bot - amount > 0:
        if type == MoneyType.RS3 or type == MoneyType.R07:
            set_amount(client.user.id, previous_amount_bot - amount, MoneyType.WagRS3 if type == MoneyType.RS3 else MoneyType.WagR07)


def get_amount(user, type):
    if user not in cache:
        if coins.find_one({"UID": str(user)}) == None:
            cache[user] = {"UID": str(user), 
            "RS3": 0.0, "R07": 0.0, "WagRS3": 0.0, "WagR07": 0.0, 
            "Tokens": 0.0, "WagWeek07": 0.0, "WagWeekRS3": 0.0}
            coins.insert_one(cache[user])
        else:
            cache[user] = coins.find_one({"UID": str(user)})
    return float(cache[user][type.name])


def update(user):
    coins.update_one({"UID": str(user)}, {"$set": cache[user]})


def set_amount(user, amount, type):
    get_amount(user, type)
    cache[user][type.name] = amount
    update(user)


client.update_amount = update_amount
client.get_amount = get_amount
client.set_amount = set_amount
client.add_cog(Rolls(client))
client.add_cog(Economy(client))
client.add_cog(DD(client))
client.add_cog(Plant(client))
client.add_cog(BlackJack(client))
client.add_cog(Cash(client))

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

if __name__  == '__main__':
    print(cache)
    client.run(config.token)