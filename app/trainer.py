# app/trainer.py
"""
Offline training helper. Use this to run experiments locally (or on Render job).
Outlines:
 - Build dataset from historical OHLC + features
 - Label outcomes (future returns)
 - Train lightgbm classifier/regressor
 - Save model to disk & serve via AI_CLOUD_ENDPOINT or integrated loader
"""
import os, joblib
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

def train_from_csv(csv_path, model_out="model.pkl"):
    # csv with features and future returns
    import pandas as pd
    df = pd.read_csv(csv_path)
    X = df[[c for c in df.columns if c.startswith("f_")]].values
    y = df["future_ret"].values
    model = GradientBoostingRegressor(n_estimators=100, max_depth=4)
    model.fit(X, y)
    joblib.dump(model, model_out)
    return model_out