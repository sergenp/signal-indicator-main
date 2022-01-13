from datetime import datetime

import numpy as np
import requests
import talib

"""DATA STRUCTURE FROM BINANCE 
[
  [
    1499040000000,      // Open time
    "0.01634790",       // Open
    "0.80000000",       // High
    "0.01575800",       // Low
    "0.01577100",       // Close
    "148976.11427815",  // Volume
    1499644799999,      // Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "17928899.62484339" // Ignore.
  ]
]
"""
def get_current_price(symbol="BTCUSDT") -> str:
  """Gets the current ticking price from the futures market for given symbol
  Parameters
  ----------
  symbol : optional
    The futures exchange symbol defaults to BTCUSDT
  """

  try:
    return requests.get(f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}").json()["price"]
  except Exception:
    return "NO INTERNET CONNECTION"

def get_data(minutes_interval, symbol="BTCUSDT") -> tuple:
  """Gets binance futures data for given symbol and calculates and returns MACD, CCI, MONEY_FLOW, RSI, STOCH SLOW D, BOLL BANDS
  Parameters
  ----------
  interval : str, required
    The kandle lines interval
  symbol : optional
    The futures exchange symbol defaults to BTCUSDT
  
  Returns
  ----------
   MACD : numpy_array, CCI : numpy_array, MONEY_FLOW:numpy_array, RSI:numpy_array, STOCH:numpy_array, [BOLLINGER BANDS]: array of numpy_array   
  """
  binance_data = requests.get(f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={minutes_interval}").json()
  _ = np.array([datetime.fromtimestamp(x[0]/1000) for x in binance_data])
  opens = np.array([x[1] for x in binance_data], dtype='f8')
  highs = np.array([x[2] for x in binance_data], dtype='f8')
  lows = np.array([x[3] for x in binance_data], dtype='f8')
  closes = np.array([x[4] for x in binance_data], dtype='f8')
  volumes = np.array([x[5] for x in binance_data], dtype='f8')

  _, _, macdhist = talib.MACD(opens, fastperiod=12, slowperiod=26, signalperiod=9)
  cci = talib.CCI(highs, lows, closes, timeperiod=14)
  rsi = talib.RSI(closes, timeperiod=14)
  money_flow = talib.MFI(highs, lows, closes, volumes, timeperiod=14)
  _, slowd = talib.STOCH(highs, lows, closes, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
  upperband, middleband, lowerband = talib.BBANDS(closes, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)

  _ = talib.CDL2CROWS(opens, highs, lows, closes)
  _ = talib.CDL3BLACKCROWS(opens, highs, lows, closes)
  _ = talib.CDL3INSIDE(opens, highs, lows, closes)

  return macdhist, cci, money_flow, rsi, slowd, [upperband, middleband, lowerband]
