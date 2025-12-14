# app/main.py
import asyncio, uvicorn, time
from fastapi import FastAPI, BackgroundTasks
from feature_engine import generate_features
from ai_interface import call_cloud_ai
from local_model import LocalModel
from risk import calculate_lot_size
from trade_executor import send_order_buy, send_order_sell
from notifier import send_telegram, format_signal
from logger_util import log_trade_line
from regime import detect_regime
from microstructure import micro_features
from config import SYMBOLS, TRADE_MODES, TRADE_THRESHOLD, RISK_PERCENT, FEATURE_COUNT

app = FastAPI(title="Qube Quant Capital - EliteQuant Cloud V4")

# models per symbol
local_models = {sym: LocalModel() for sym in SYMBOLS}
last_scores = {sym: 0.0 for sym in SYMBOLS}
smoothed = {sym: 0.0 for sym in SYMBOLS}
MODE = "auto"

# background worker
async def worker_loop():
    while True:
        for sym in SYMBOLS:
            try:
                # 1) features
                feats = generate_features(sym)
                # 2) micro
                micro = micro_features(sym)
                # 3) regime
                reg = detect_regime(sym)
                # 4) ai cloud
                ai_score = call_cloud_ai(feats)
                if ai_score is None:
                    # fallback to local model
                    ai_score = local_models[sym].predict(feats)
                # 5) local model
                local_score = local_models[sym].predict(feats)
                # 6) hybrid final score
                final_raw = 0.4*local_score + 0.5*ai_score + 0.1*(reg["score"]*2-1)
                # 7) smoothing
                smoothed[sym] = local_models[sym].smooth(smoothed[sym], final_raw)
                last_scores[sym] = final_raw
                # 8) logging
                log_trade_line("signals_log.csv", f"{sym},{local_score:.4f},{ai_score:.4f},{final_raw:.4f}")
                # 9) decision
                abs_score = abs(smoothed[sym])
                if abs_score >= TRADE_THRESHOLD:
                    # choose side
                    side = "BUY" if smoothed[sym] > 0 else "SELL"
                    # compute stop pips from ATR-ish
                    # We estimate stop_pips conservatively
                    stop_pips = max(8.0, 0.0005*1e4) # placeholder
                    # lot sizing: we assume an account balance (you will supply in real system)
                    account_balance = 10.0  # USER MUST SET when connecting to real broker
                    stop_loss_points = stop_pips  # placeholder
                    lots = calculate_lot_size(account_balance, stop_loss_points, sym)
                    # entry prices: placeholders
                    sl = 0.0; tp = 0.0
                    if side == "BUY":
                        # Simulate ask price fetch
                        price = 1.0
                        sl = price - stop_pips*0.0001
                        tp = price + stop_pips*0.0001*2
                        # attempt execution (placeholder)
                        resp = send_order_buy(sym, lots, sl, tp, "AutoTrade")
                    else:
                        price = 1.0
                        sl = price + stop_pips*0.0001
                        tp = price - stop_pips*0.0001*2
                        resp = send_order_sell(sym, lots, sl, tp, "AutoTrade")
                    # send Telegram
                    text = format_signal(sym, side, lots, sl, tp, final_raw, MODE, notes="QubeQuant V4 auto-signal")
                    send_telegram(text)
                # 10) small online update of local model from pseudo-reward (placeholder)
                # if you later track filled trades and PnL, call local_models[sym].update(feats,reward)
            except Exception as e:
                print("Error in worker for", sym, e)
        # sleep until next H1 bar processing
        await asyncio.sleep(60*60)  # process once per H1 by default

@app.on_event("startup")
async def startup_event():
    # start background worker
    asyncio.create_task(worker_loop())

@app.get("/")
def read_root():
    return {"status":"ok","service":"Qube Quant Capital EliteQuant V4"}

@app.get("/health")
def health():
    return {"status":"healthy","symbols":len(SYMBOLS)}

@app.post("/predict")
def predict_endpoint(symbol: str):
    feats = generate_features(symbol)
    ai_score = call_cloud_ai(feats)
    local = local_models[symbol].predict(feats)
    final = 0.4*local + 0.5*(ai_score if ai_score is not None else local) + 0.1*detect_regime(symbol)["score"]
    return {"symbol":symbol,"local":local,"ai":ai_score,"final":final}