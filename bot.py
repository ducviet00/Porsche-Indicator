import asyncio
import ccxt
import time
import numpy as np
from tqdm import tqdm
import discord
from utils.moving_average import calculate_MA
TOKEN = ''
CHANNEL_ID = 819248630908846152


class Porsche(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        exchange_id = 'binance'
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class({
            'timeout': 30000,
            'enableRateLimit': True,
        })
        self.exchange.load_markets()
        self.watching_pairs = ['BTC/USDT']
        self.MA7_alerted = []
        self.MA25_alerted = []
        # create the background task and run it in the background
        self.noti = self.loop.create_task(self.see_the_future())
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
            for symbol in self.watching_pairs:
                ohlcv_prices = self.exchange.fetchOHLCV(symbol, '1d')
                await asyncio.sleep(self.exchange.rateLimit / 1000)
                last_price = ohlcv_prices[-1][4]
                MA7, alert_7, MA25, alert_25 = calculate_MA(ohlcv_prices)
                if alert_25 and symbol not in self.MA25_alerted:
                    self.MA25_alerted.append(symbol)
                    await channel.send(f"{symbol} is close to MA25 line, last price is {last_price:.2f}, MA25 price is {MA25:.2f}")
                if alert_7 and symbol not in self.MA7_alerted:
                    self.MA7_alerted.append(symbol)
                    await channel.send(f"{symbol} is close to MA7 line, last price is {last_price:.2f}, MA7 price is {MA7:.2f}")
                print(f"{symbol}: {last_price:.2f}")
            # await channel.send("Bot is still running")
            await asyncio.sleep(300)  # task runs every 5 minutes

    async def update_pairs(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)
        self.watching_pairs = []
        while not self.is_closed():
            btcusdt = self.exchange.fetchTicker('BTC/USDT')['last']
            for symbol in tqdm(self.exchange.markets):
                if '/USDT' not in symbol:
                    continue
                # time.sleep wants seconds
                time.sleep(self.exchange.rateLimit / 1000)
                info = self.exchange.fetchTicker(symbol)
                if 50 < info['quoteVolume'] / btcusdt < 400 or info['quoteVolume'] / btcusdt > 10000:
                    self.watching_pairs.append(symbol)
            self.MA7_alerted = []
            self.MA25_alerted = []
            await channel.send(f"Size of watching token list {len(self.watching_pairs)}")
            await asyncio.sleep(3600)


porsche = Porsche()
porsche.run(TOKEN)
