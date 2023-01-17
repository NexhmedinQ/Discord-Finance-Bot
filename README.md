## Installation
1. Python 3.6 or above is required.
2. Run `git clone git@github.com:NexhmedinQ/Discord-Finance-Bot.git`
3. Run `pip install -r requirements.txt`
4. In a `.env` file place the discord token.
5. Change the dsn in the `create_db_pool` function in `bot.py` to connect the bot to your own database. 
6. Run the bot with `python3 bot.py`. 

## Usage and Features
`!curr_price` - Returns the latest price of of ticker/s specified. 
