# app/regime.py
"""
Regime detection module — uses ATR & ADX-like heuristics to classify regime.
Outputs:
 - regime_score (0..1) numeric weight
 - regime_class (-1,0,1) discrete
"""
import math
from feature_engine import generate_features, compute_atr, fetch_ohlc

def detect_regime(symbol):
    data = fetch_ohlc(symbol, timeframe="1h", limit=200)
    close = data["close"]
    high = data["high"]
    low = data["low"]
    atr = compute_atr(high, low, close, 14)
    # simple adx analog: use momentum magnitude
    mom = abs(close[-1] - close[-10]) if len(close)>10 else 0.0
    # compute scores
    a = min(1.0, mom / (close[-1]*0.01 + 1e-9))
    v = min(1.0, atr / (close[-1]*0.01 + 1e-9))
    regime_score = 0.6 * a + 0.4 * v
    # class:
    if a > 0.4 and v > 0.002: cls = 1
    elif a < 0.05 and v < 0.0005: cls = 0
    else: cls = 0
    return {"score": float(regime_score), "class": int(cls)}