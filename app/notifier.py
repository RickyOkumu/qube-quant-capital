# app/notifier.py
"""
Telegram notifier for signals. Works without broker integration, so you can
receive trade signals on your phone.
"""
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram(text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode":"Markdown"}
        r = requests.post(url, json=payload, timeout=10)
        return r.ok
    except Exception as e:
        print("Telegram error", e)
        return False

def format_signal(symbol, side, lots, sl, tp, score, mode, notes=""):
    return (f"*Qube Quant Capital — SIGNAL*\n"
            f"Symbol: `{symbol}`\n"
            f"Mode: `{mode}`\n"
            f"Side: `{side}`\n"
            f"Lots: `{lots}`\n"
            f"SL: `{sl}`  TP: `{tp}`\n"
            f"Score: `{score:.3f}`\n"
            f"{notes}")