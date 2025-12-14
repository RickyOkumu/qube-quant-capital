# app/logger_util.py
import csv, os, time

def log_trade_line(fname, line: str):
    with open(fname, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M')}," + line + "\n")