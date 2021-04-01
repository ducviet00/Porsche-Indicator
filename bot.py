import asyncio
import ccxt
import time
import numpy as np
from tqdm import tqdm
import discord
from discord.ext import commands
from utils.get_emoji import get_emoji
from utils import calculate_MA, calculate_RSI

TOKEN = ''
CHANNEL_ID = 819248630908846152

tuanlu = '<:tuanlu:823863394188394496>'
flexing = '<:flexing:824860288389087273>'
bot = commands.Bot(command_prefix='$')
class Porsche(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.exchange = ccxt.binance({
            'enableRateLimit': True,  # required https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
            'options': {
                'defaultType': 'spot',
            },
        })
        self.exchange.load_markets()
        self.exchange_futures = ccxt.binance({
            'enableRateLimit': True,  # required https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
            'options': {
                'defaultType': 'future',
            },
        })
        self.exchange_futures.load_markets()
        self.fixed_list = ['BTC/USDT', 'ETH/USDT', 'RSR/USDT']
        self.watching_pairs = []
        self.MA7_alerted = []
        self.MA25_alerted = []
        # create the background task and run it in the background
        self.rsi_noti = self.loop.create_task(self.rsi_noti())
        self.ma_noti = self.loop.create_task(self.see_the_future())
        self.update = self.loop.create_task(self.update_pairs())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def see_the_future(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)  # channel ID goes here
        while not self.is_closed():
            for symbol in self.watching_pairs + self.fixed_list:
                for tf in ['1d', '1w']:
                    ohlcv_prices = self.exchange.fetchOHLCV(symbol, tf)
                    await asyncio.sleep(self.exchange.rateLimit / 1000)
                    last_price = ohlcv_prices[-1][4]
                    MA7, alert_7, MA25, alert_25 = calculate_MA(ohlcv_prices)
                    
                    if alert_25 and symbol not in self.MA25_alerted:
                        self.MA25_alerted.append(symbol)
                        emoji = get_emoji(last_price, MA25)
                        await channel.send(f"TF{tf.upper()}{emoji}: {symbol} is close to MA25 line, last price is {last_price:.7g}, MA25 price is {MA25:.7g}")
                    if alert_7 and symbol not in self.MA7_alerted:
                        self.MA7_alerted.append(symbol)
                        emoji = get_emoji(last_price, MA7)
                        await channel.send(f"TF{tf.upper()}{emoji}: {symbol} is close to MA7 line, last price is {last_price:.7g}, MA7 price is {MA7:.7g}")
                    print(f"TF{tf.upper()}{symbol}: Price {last_price}")
            # await channel.send("Bot is still running")
            await asyncio.sleep(900)  # task runs every 15 minutes

    async def rsi_noti(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)  # channel ID goes here
        while not self.is_closed():
            for symbol in self.exchange_futures.markets:
                if '/USDT' not in symbol:
                    continue
                for tf in ['5m', '15m', '1h', '4h']:
                    ohlcv_prices = self.exchange.fetchOHLCV(symbol, tf)
                    await asyncio.sleep(self.exchange.rateLimit / 1000)
                    rsi_14 = calculate_RSI(ohlcv_prices, n=14)
                    if rsi_14 > 80:
                        await channel.send(f"TF{tf.upper()}: {symbol}: RSI: {rsi_14}")
                    if rsi_14 < 20:
                        await channel.send(f"TF{tf.upper()}: {symbol}: RSI: {rsi_14}")
                    print(f"TF{tf.upper()}{symbol}: RSI14 {rsi_14}")
            await asyncio.sleep(300)  # task runs every 5 minutes

    async def update_pairs(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)
        while not self.is_closed():
            self.watching_pairs = []
            btcusdt = self.exchange.fetchTicker('BTC/USDT')['last']
            for symbol in tqdm(self.exchange.markets):
                if '/USDT' not in symbol:
                    continue
                if 'UP/' in symbol or 'DOWN/' in symbol or 'USD/' in symbol:
                    continue
                # time.sleep wants seconds
                time.sleep(self.exchange.rateLimit / 1000)
                info = self.exchange.fetchTicker(symbol)
                if 50 < info['quoteVolume'] / btcusdt < 100:
                    self.watching_pairs.append(symbol)
            self.MA7_alerted = []
            self.MA25_alerted = []
            await channel.send(f"Size of watching token list {len(self.watching_pairs)}")
            await asyncio.sleep(7200)

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return
        if message.content.startswith('$add'):
            _, symbol = message.content.split(" ")
            if symbol in self.fixed_list:
                await message.channel.send(f'{symbol} is already in watching list {tuanlu}.')
            elif symbol not in self.exchange.markets:
                await message.channel.send(f'{self.exchange.name} doesn\'t have {symbol} pair {tuanlu}: .')
            else:
                self.fixed_list.append(symbol)
                await message.channel.send(f'Successful adding {symbol} into watching list  {flexing}.')

        if message.content.startswith('$rm'):
            _, symbol = message.content.split(" ")
            if symbol in self.fixed_list:
                self.fixed_list.remove(symbol)
                await message.channel.send(f'Successful removing {symbol} from watching list {flexing}.')
            else:
                await message.channel.send(f'{symbol} is not in watching list {tuanlu}:.')
                

            
porsche = Porsche()
porsche.run(TOKEN)
