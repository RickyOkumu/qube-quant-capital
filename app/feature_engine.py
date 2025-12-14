# app/feature_engine.py
"""
Feature engineering: multi-TF indicator extraction similar to the C++ version.
This module uses MT5-like indicator functions via Python wrappers is not possible
here, so we use a simple approach with price candles from a public data source.

We will use a simple exchange prices source (Alpha Vantage or other). For demo,
we use a local simulated price feed (placeholder). On Render, you should hook a
real market data API or broker API.
"""
from typing import List
import math
import numpy as np
from config import FEATURE_COUNT, SYMBOLS

# Helper functions
def clamp(x, lo=-3.0, hi=3.0):
    return max(lo, min(hi, x))

def normalize_feat(x):
    return clamp(x) / 3.0

# Price fetch placeholder - returns fake OHLC arrays or integrate with real data
def fetch_ohlc(symbol: str, timeframe: str = "1h", limit: int = 200):
    """
    TODO: Replace with real data fetch (Alpha Vantage, Twelve Data, broker REST).
    For now, this returns synthetic data for testing.
    """
    # Synthetic: small random walk
    import random, time
    base = 1.0 + (hash(symbol) % 100)/10000.0
    prices = [base + 0.0001*random.gauss(0,1) for _ in range(limit)]
    # Make OHLC arrays
    o = prices[:-1]
    c = prices[1:]
    h = [max(a,b)*(1+0.0001*random.random()) for a,b in zip(o,c)]
    l = [min(a,b)*(1-0.0001*random.random()) for a,b in zip(o,c)]
    vol = [100 + random.randint(0,50) for _ in range(limit)]
    return {"open": o, "high": h, "low": l, "close": c, "volume": vol, "timestamps": list(range(limit))}

def compute_atr(high, low, close, period=14):
    trs = []
    for i in range(1, len(close)):
        tr = max(high[i]-low[i], abs(high[i]-close[i-1]), abs(low[i]-close[i-1]))
        trs.append(tr)
    if len(trs) < period:
        return float(np.mean(trs)) if trs else 0.0
    return float(np.mean(trs[-period:]))

def compute_rsi(close, period=14):
    deltas = np.diff(np.array(close))
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum()/period
    down = -seed[seed < 0].sum()/period
    rs = up/down if down != 0 else 0
    rsi = 100 - (100/(1+rs)) if down !=0 else 100.0
    return float(rsi)

def compute_sma(arr, period):
    if len(arr) < period: return float(np.mean(arr))
    return float(np.mean(arr[-period:]))

def generate_features(symbol: str) -> List[float]:
    """
    Returns fixed FEATURE_COUNT vector
    """
    data = fetch_ohlc(symbol, timeframe="1h", limit=200)
    close = data["close"]
    high = data["high"]
    low = data["low"]
    vol = data["volume"]
    # basic indicators
    ma5 = compute_sma(close, 5)
    ma21 = compute_sma(close, 21)
    ma50 = compute_sma(close, 50)
    rsi14 = compute_rsi(close, 14)
    # m15 rsi (approx from same series)
    rsi7 = compute_rsi(close[-50:], 7) if len(close) >= 50 else rsi14
    atr14 = compute_atr(high, low, close, 14)
    # make features array
    f = [0.0]*FEATURE_COUNT
    p = close[-1] if close else 1.0
    f[0] = normalize_feat(ma5/p)
    f[1] = normalize_feat(ma21/p)
    f[2] = normalize_feat((ma5 - ma21)/p)
    f[3] = normalize_feat((rsi14-50.0)/50.0)
    f[4] = normalize_feat((rsi7-50.0)/50.0)
    f[5] = normalize_feat(0.01) # ADX placeholder
    f[6] = normalize_feat(atr14/(p*0.01+1e-9))
    f[7] = normalize_feat((max(high[-1], low[-1]) - min(high[-1], low[-1]))/p)
    f[8] = normalize_feat( (close[-1] - ( (high[-1]+low[-1])/2.0) ) / ( (max(high[-1],low[-1]) - min(high[-1],low[-1])) + 1e-9))
    f[9] = normalize_feat(0.0001)  # spread placeholder
    # micro features
    f[10] = normalize_feat((vol[-1] if vol else 1)/100.0)
    # fill remaining with recent returns
    for i in range(11, FEATURE_COUNT):
        idx = -1 - (i-11)
        if abs(idx) <= len(close):
            ret = (close[idx] - close[idx-1]) / (p + 1e-9) if len(close) > abs(idx)+1 else 0.0
            f[i] = normalize_feat(ret)
        else:
            f[i] = 0.0
    return f