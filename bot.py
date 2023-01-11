import os
import random
from dotenv import load_dotenv

import discord
from discord.ext import commands
import data
from table2ascii import table2ascii as t2a, PresetStyle
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='curr_price', help='Get the current price of one or more stocks')
async def curr_price(ctx, *args):
    ret_array = []
    for tag in args:
        ret_array.append([str(tag), f"${round(data.current_price(str(tag)), 2)}"])

    output = t2a(
        header=["Ticker", "Price"],
        body=[arr for arr in ret_array],
        style=PresetStyle.thin_compact
    )

    await ctx.send(f"```\n{output}\n```")
    
    
@bot.command(name='info', help='Get info of a particular stock according to the list of keys')
async def get_info(ctx, symbol: str, key: str):
    await ctx.reply(data.get_info(symbol, key))

bot.run(TOKEN)

# command to get % change in a certain sector ? 
# command for % change in stock price over a specified time period
# command to get a graph of a stock
# command to get prices of stocks
# command for balance sheet

