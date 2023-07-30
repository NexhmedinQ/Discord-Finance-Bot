from asyncio import sleep, run
import os
import random
from dotenv import load_dotenv

import discord
from discord.ext import commands, tasks
import data
from table2ascii import table2ascii as t2a, PresetStyle
import asyncpg 
from datetime import datetime, timedelta

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)


async def create_db_pool():
    bot.db = await asyncpg.create_pool(dsn="postgres://postgres:database@localhost:5432/finance_bot")
    print("connected to db")

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
    print("calling")
    if not data.ticker_exists(symbol):
        await ctx.send(f"Ticker symbol {symbol} does not exist or may be delisted.")
        return
    print("calling2")
    bsheet = data.get_balance_sheet(symbol)
    print("calling3")
    for i in range(0, 4):
        print("calling4")
        sheet1 = bsheet[int((i / 4) * len(bsheet)):int(len(bsheet) * ((i + 1) / 4))]
        output = t2a(
            body=[arr for arr in sheet1],
            style=PresetStyle.thin_compact
        )
        await ctx.send(f"```\n{output}\n```") 

@balance_sheet.error
async def bsheet_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Incorrect arguments entered. Please enter: !balance_sheet \{ticker symbol\}")
    
@bot.command(name='earnings', help='Returns a graph of a companies revenue and earnings over the past 4 years')  
async def earnings(ctx, symbol: str):
    if not data.ticker_exists(symbol):
        await ctx.send(f"Ticker symbol {symbol} does not exist or may be delisted.")
        return
    url = data.get_earnings(symbol, False)
    embed = discord.Embed(title=f"{symbol} Earnings") 
    embed.set_image(url=url)
    await ctx.send(embed=embed)

@earnings.error
async def earnings_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Incorrect arguments entered. Please enter: !earnings \{ticker symbol\}")
    
@bot.command(name='quarterly_earnings', help='Returns a graph of a companies revenue and earnings over the past 4 quarters')  
async def quarterly_earnings(ctx, symbol: str):
    if not data.ticker_exists(symbol):
        await ctx.send(f"Ticker symbol {symbol} does not exist or may be delisted.")
        return
    url = data.get_earnings(symbol, True)
    embed = discord.Embed(title=f"{symbol} Earnings") 
    embed.set_image(url=url)
    await ctx.send(embed=embed)

@quarterly_earnings.error
async def qearnings_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Incorrect arguments entered. Please enter: !quarterly_earnings \{ticker symbol\}")

@bot.command(name='add_news', help='Adds a ticker to get daily news for')  
async def add_news(ctx, symbol: str):
    if not data.ticker_exists(symbol):
        await ctx.send(f"Ticker symbol {symbol} does not exist or may be delisted.")
        return
    check_ticker = await bot.db.fetch('SELECT ticker FROM news_tickers WHERE ticker = $1', symbol)
    if len(check_ticker) > 0:
        await ctx.send(f"Ticker symbol {symbol} has already been added")
    else:
        await bot.db.execute('INSERT INTO news_tickers(ticker) VALUES ($1)', symbol)
        
@tasks.loop(hours=24)  
async def daily_news(ctx):
    tickers = await bot.db.fetch('SELECT ticker FROM news_tickers')
    ticker_array = [ticker[0] for ticker in tickers]
    news = data.get_news(ticker_array)
    set_of = set(ticker_array)
    for article in news.values():
        related_tickers = [company for company in article['relatedTickers'] if company in set_of]
        ticker_string = ", ".join(related_tickers)
        publisher = article['publisher']
        thumbnail = None
        
        try:
            thumbnail = article['thumbnail']['resolution'][0]['url']
        except KeyError:
            pass
        
        embed=discord.Embed(title=article['title'], url=article['link'], color=0x00ffff)
        
        if thumbnail: 
            embed.set_thumbnail(url=thumbnail)
        
        embed.add_field(name="Publisher", value=publisher, inline=False)
        embed.add_field(name="Related Tickers", value=ticker_string, inline=True)
        await ctx.send(embed=embed)

@daily_news.before_loop
async def before_daily_news():
    now = datetime.now()
    current_hour = now.strftime("%H") 
    if int(current_hour) > 8:
        nine_am = (now + timedelta(days=1)).replace(hour=9, minute=0, microsecond=0, second=0)
    else:
        nine_am = datetime(year=int(now.strftime("%Y")), month=int(now.strftime("%m")), day=int(now.strftime("%d")), hour=9)
    diff = (nine_am - now).seconds
    await sleep(diff)

@bot.command(name="remove_news", help="Remove a ticker from the news watchlist")
async def remove_news(ctx, symbol: str):
    tickers = await bot.db.fetch('SELECT ticker FROM news_tickers')
    ticker_array = [ticker[0] for ticker in tickers]
    if symbol not in ticker_array:
        await ctx.send(f"Ticker {symbol} is not in the watchlist.")
    else:
        await bot.db.execute('''DELETE FROM news_tickers where ticker = $1''', symbol)

async def main():
    await create_db_pool() 
    await bot.start(TOKEN)

run(main())



