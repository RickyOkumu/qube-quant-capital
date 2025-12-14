# app/risk.py
"""
Risk management & lot sizing. Uses tick value if attached to broker API.
For demo returns conservative sizing for small accounts.
"""
from config import RISK_PERCENT
import math

def calculate_lot_size(account_balance: float, stop_loss_points: float, symbol: str, min_lot=0.01, max_lot=1.0):
    # If we don't have real tick value, assume $10 per pip per lot for majors (approx).
    # stop_loss_points is in points (i.e., price difference / point)
    value_per_point_per_lot = 10.0
    loss_per_lot = abs(stop_loss_points) * value_per_point_per_lot
    if loss_per_lot <= 0:
        loss_per_lot = 1.0
    risk_amount = account_balance * (RISK_PERCENT / 100.0)
    raw_lots = risk_amount / loss_per_lot
    # round to 2 decimal
    lots = math.floor(raw_lots * 100)/100.0
    lots = max(min_lot, min(lots, max_lot))
    return lots