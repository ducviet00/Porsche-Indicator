import numpy as np

def calculate_MA(ohlcv_prices):
    ohlcv_prices = np.array(ohlcv_prices)
    last_price = ohlcv_prices[-1, 4]
    MA7 = np.mean(ohlcv_prices[-7:, 4])
    MA25 = np.mean(ohlcv_prices[-25:, 4])
    alert_7 = False
    alert_25 = False
    if last_price > MA7*1.01 and last_price < MA7*1.01:
        alert_7 = True
    if last_price > MA25*1.01 and last_price < MA25*1.01:
        alert_25 = True
    return MA7, alert_7, MA25, alert_25
