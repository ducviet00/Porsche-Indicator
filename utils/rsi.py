import numpy as np
import pandas as pd

# Thank to https://stackoverflow.com/a/57037866
def rma(x, n, y0):
    a = (n-1) / n
    ak = a**np.arange(len(x)-1, -1, -1)
    return np.r_[np.full(n, np.nan), y0, np.cumsum(ak * x) / ak / n + y0 * a**np.arange(1, len(x)+1)]


def calculate_RSI(ohlcv_prices, n=14):
    df = pd.DataFrame(ohlcv_prices, columns=[
                      'Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Change'] = df['Close'].diff()
    df['Gain'] = df.Change.mask(df.Change < 0, 0.0)
    df['Loss'] = -df.Change.mask(df.Change > 0, -0.0)
    df['Avg_Gain'] = rma(df.Gain[n+1:].to_numpy(), n,
                        np.nansum(df.Gain.to_numpy()[:n+1])/n)
    df['Avg_Loss'] = rma(df.Loss[n+1:].to_numpy(), n,
                        np.nansum(df.Loss.to_numpy()[:n+1])/n)
    df['RS'] = df.Avg_Gain / df.Avg_Loss
    df['RSI_14'] = 100 - (100 / (1 + df.RS))

    return df.iloc[-1]['RSI_14']
    
    
