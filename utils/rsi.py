import numpy as np
def calculate_RSI(ohlcv_prices):
    # Not complete yet
    ohlcv_prices = np.array(ohlcv_prices)
    last_price = ohlcv_prices[-1, 4]
    close_prices = ohlcv_prices[:, 4]
    
    