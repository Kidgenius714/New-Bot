import asyncio
import atexit
import io
import json
import random
import hmac
import hashlib
from hashlib import sha256
from threading import Timer

import pymongo
from discord import Colour, Embed
from discord.ext import commands

from commands.Blackjack import BlackJack
from commands.CashinOut import Cash
from commands.Chest import Chest
from commands.Dice_Duel import DD
from commands.Economy import Economy
from commands.FlowerPoker import FlowerPoker
from commands.OverUnder import OverUnder
from commands.Plant import Plant
from commands.Rolls import Rolls
from commands.Secret import Secret
from economy.Money_type import MoneyType

CONFIG_NAME = "config.json"

with open(CONFIG_NAME, 'r') as datafile, io.StringIO() as data:
    config = json.load(datafile)


def add_default(con, prop, default):
    if prop not in con:
        con[prop] = default


add_default(config, "token", "<INSERT_TOKEN_HERE>")
add_default(config, "prefix", "!")
add_default(config, "mongo_url", "<INSERT_MONGO_URL_HERE>")
add_default(config, "mongo_database", "<INSERT_DATABASE_NAME_HERE>")
add_default(config, "mongo_collection", "<INSERT_COLLECTION_NAME_HERE>")
add_default(config, "secret_hash_channel_id", "<INSERT_SECRET_LOG_CHANNEL_ID>")
add_default(config, "request_channel_id", "<INSERT_CASHIN/CASHOUT_ID>")
add_default(config, "cashier_channel_id", "<INSERT_CASHIN/CASHOUT_CASHIER_HERE>")
add_default(config, "cashier_role_id", "<INSERT_CASHIN/CASHOUT_CASHIER_ID_HERE>")
add_default(config, "can_modify_economy", "<PEOPLE_CAN_USE_SET/UPDATE_ECONOMY>")
add_default(config, "card_names", [
    {
        "emoji": "<:BetaGate2_Key1_Clue_HyKwIEkVVxk4:662527301669486617>",
        "value": 2
    }
])

hash = str(hex(random.getrandbits(256)))[2:]
m = sha256()
m.update(hash.encode('utf-8'))
add_default(config, "unhash", hash)
add_default(config, "hash", m.hexdigest())
add_default(config, "flowers", [
    "<:yellow:563801080484462596>",
    "<:red:563801174952902696>",
    "<:purple:563801460047872031>",
    "<:pastle:563800526744059926>",
    "<:orange:563801131990384642>",
    "<:blue:563800489628794890>",
    "<:rainbow:563800536063803393>"
])

with open(CONFIG_NAME, 'w') as datafile:
    json.dump(config, datafile, indent=2)

client = commands.Bot(command_prefix=config["prefix"], case_insensitive=True)
mongo_client = pymongo.MongoClient(config['mongo_url'])
coins = mongo_client[config['mongo_database']][config['mongo_collection']]

cache = {}
nonce = {}


def update_amount(user, amount, money_type):
    previous_amount = get_amount(user, money_type)
    set_amount(user, previous_amount + amount, money_type)

    if user == client.user.id:
        return

    previous_amount_bot = get_amount(client.user.id, money_type)
    set_amount(client.user.id, previous_amount_bot - amount, money_type)


def wagered(user, amount, money_type):
    if money_type == MoneyType.RS3 or money_type == MoneyType.R07:
        previous_amount_bot = get_amount(user, MoneyType.WagRS3 if money_type == MoneyType.RS3 else MoneyType.WagR07)
        set_amount(user, previous_amount_bot + amount,
                   MoneyType.WagRS3 if money_type == MoneyType.RS3 else MoneyType.WagR07)


def get_amount(user, money_type):
    cache_check(user)
    return float(cache[user][money_type.name])

def cache_check(user):
    if user not in cache:
        if coins.find_one({"UID": str(user)}) is None:
            cache[user] = {"UID": str(user),
                           "RS3": 0.0, "R07": 0.0,
                           "WagRS3": 0.0, "WagR07": 0.0,
                           "Tokens": 0.0, "secret": str(hex(random.getrandbits(256)))[2:],
                           "WagWeek07": 0.0, "WagWeekRS3": 0.0}
            coins.insert_one(cache[user])
        else:
            cache[user] = coins.find_one({"UID": str(user)})



def update(user):
    coins.update_one({"UID": str(user)}, {"$set": cache[user]})


def set_amount(user, amount, money_type):
    get_amount(user, money_type)
    cache[user][money_type.name] = amount

def set_secret(user, sec):
    cache_check(user)

    cache[user]["secret"] = sec

def contains_secret(sec):
    for i in cache:
        if "secret" in cache[i]:
            if cache[i]["secret"] == sec:
                return True

    found = coins.find_one({"secret": sec})
    if found is None:
        return False
    return found["UID"] not in cache

def get_secret_nonce(user):
    cache_check(user)

    if "secret" not in cache[user]:
        cache[user]["secret"] = str(hex(random.getrandbits(256)))[2:]

    if user not in nonce:
        nonce[user] = 0

    return (cache[user]["secret"], nonce[user])

def update_nonce(user):
    cache_check(user)

    if user not in nonce:
        nonce[user] = 0

    nonce[user] = nonce[user] + 1

async def checking_database(ctx):
    embed = Embed(colour=Colour.gold(), description=f"Checking database")
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    return await ctx.send(embed=embed)

def random_number(user):

    if "secret" not in cache[user]:
        cache[user]["secret"] = str(hex(random.getrandbits(256)))[2:]

    if user not in nonce:
        nonce[user] = 0

    hash = hmac.new(config["unhash"].encode("utf-8"), cache[user]["secret"].encode("utf-8") + "-".encode("utf-8") + str(nonce[user]).encode("utf-8"), hashlib.sha512).hexdigest()
    update_nonce(user)

    offset = 5

    while int(hash[offset-5:offset], 16) > 999999:
        offset += 5

    return int(hash[offset-5:offset], 16)%(10000)/100


client.config = config
client.update_amount = update_amount
client.get_amount = get_amount
client.set_amount = set_amount
client.wagered = wagered
client.set_secret = set_secret
client.contains_secret = contains_secret
client.get_secret_nonce = get_secret_nonce
client.random_number = random_number
client.checking_database = checking_database
client.add_cog(Rolls(client))
client.add_cog(Economy(client))
client.add_cog(DD(client))
client.add_cog(Plant(client))
client.add_cog(BlackJack(client))
client.add_cog(Cash(client))
client.add_cog(OverUnder(client))
client.add_cog(FlowerPoker(client))
client.add_cog(Chest(client))
client.add_cog(Secret(client))

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    save()
    await regenerate_hash()


def on_exit():
    print("Saving!")
    for user in cache:
        coins.update_one({"UID": str(user)}, {"$set": cache[user]})
    with open(CONFIG_NAME, 'w') as datafile:
        json.dump(config, datafile, indent=2)


atexit.register(on_exit)

async def regenerate_hash():

    hash = str(hex(random.getrandbits(256)))[2:]
    m = sha256()
    m.update(hash.encode('utf-8'))

    nonce.clear()

    print("Previous hash: " + config["hash"])
    print("Previous unhash: " + config["unhash"])
    print("New unhash: " + hash)
    print("New hash: " + m.hexdigest())
    print()

    if client.get_channel(config["secret_hash_channel_id"]) is None:
        raise LookupError("Cannot find channel with id " + config["secret_hash_channel_id"])

    embed = Embed(colour=Colour.green())
    embed.add_field(name="Previous hash",
                    value=config["hash"], inline=False)
    embed.add_field(name="Previous unhash",
                    value=config["unhash"], inline=False)
    embed.add_field(name="New hash",
                    value=m.hexdigest(), inline=False)
    await client.get_channel(config["secret_hash_channel_id"]).send(embed=embed)

    config["hash"] = m.hexdigest()
    config["unhash"] = hash

    await asyncio.sleep(60 * 60 *12)
    await regenerate_hash()


def save():
    for user in cache:
        coins.update_one({"UID": str(user)}, {"$set": cache[user]})

    Timer(60 * 60, save).start()


if __name__ == '__main__':
    client.run(config['token'])
