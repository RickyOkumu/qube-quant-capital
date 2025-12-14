# app/local_model.py
"""
Local lightweight model (linear weights) with online updates.
This is the "local ML" that can do small updates in service.
"""
import math
from typing import List
from config import FEATURE_COUNT
import random

class LocalModel:
    def __init__(self):
        # initialize weights small random
        self.w = [0.0] * FEATURE_COUNT
        # you could load from disk if available
        self.smoothing = 0.85

    def predict(self, features: List[float]) -> float:
        s = 0.0
        for i in range(min(len(features), len(self.w))):
            s += self.w[i] * features[i]
        # sigmoid to -1..1
        score = 1/(1+math.exp(-s)) if s>=0 else math.exp(s)/(1+math.exp(s))
        return (score - 0.5)*2.0

    def update(self, features: List[float], reward: float, lr=1e-4):
        for i in range(min(len(features), len(self.w))):
            self.w[i] += lr * reward * features[i]
        # tiny decay
        for i in range(len(self.w)):
            self.w[i] *= 0.9999

    def smooth(self, prev: float, curr: float) -> float:
        return self.smoothing*prev + (1.0-self.smoothing)*curr