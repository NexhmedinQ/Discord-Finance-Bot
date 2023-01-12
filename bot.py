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
    non_existent = []
    for tag in args:
        if data.ticker_exists(str(tag)):
            ret_array.append([str(tag), f"${round(data.current_price(str(tag)), 2)}"])
        else:
            non_existent.append(str(tag))

    output = t2a(
        header=["Ticker", "Price"],
        body=[arr for arr in ret_array],
        style=PresetStyle.thin_compact
    )

    await ctx.send(f"```\n{output}\n```")
    
    if len(non_existent) > 0:
        await ctx.send(f"{', '.join(non_existent)} symbol/s do not exist")

    
    
@bot.command(name='info', help='Get info of a particular stock according to the list of keys')
async def get_info(ctx, symbol: str, key: str):
    if not data.ticker_exists(symbol):
        await ctx.send(f"Ticker symbol {symbol} does not exist or may be delisted.")
    else:
        try:
            await ctx.send(data.get_info(symbol, key))
        except KeyError:
            await ctx.send(f"{key} is not a valid information identifier")
            
@get_info.error
async def info_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Incorrect arguments entered. Please enter: !get_info \{ticker symbol\} \{information requested\}")
        
        
@bot.command(name='balance_sheet', help='Returns the most recent balance sheet of a single company specified by the ticker symbol entered')
async def balance_sheet(ctx, symbol: str):
    if not data.ticker_exists(symbol):
        await ctx.send(f"Ticker symbol {symbol} does not exist or may be delisted.")
        return
    
    bsheet = data.get_balance_sheet(symbol)
    
    for i in range(0, 4):
        sheet1 = bsheet[int((i / 4) * len(bsheet)):int(len(bsheet) * ((i + 1) / 4))]
        output = t2a(
            body=[arr for arr in sheet1],
            style=PresetStyle.thin_compact
        )
        await ctx.send(f"```\n{output}\n```") 
    
@bot.command(name='earnings', help='Returns a graph of a companies revenue and earnings over the past 4 years')  
async def earnings(ctx, symbol: str):
    if not data.ticker_exists(symbol):
        await ctx.send(f"Ticker symbol {symbol} does not exist or may be delisted.")
        return
    url = data.get_earnings(symbol, False)
    embed = discord.Embed(title=f"{symbol} Earnings") 
    embed.set_image(url=url)
    await ctx.send(embed=embed)
    
@bot.command(name='quarterly_earnings', help='Returns a graph of a companies revenue and earnings over the past 4 quarters')  
async def quarterly_earnings(ctx, symbol: str):
    if not data.ticker_exists(symbol):
        await ctx.send(f"Ticker symbol {symbol} does not exist or may be delisted.")
        return
    url = data.get_earnings(symbol, True)
    embed = discord.Embed(title=f"{symbol} Earnings") 
    embed.set_image(url=url)
    await ctx.send(embed=embed)

bot.run(TOKEN)

# command for % change in stock price over a specified time period
# command to get a graph of a stock
# command for analyst recommandations and predictions


