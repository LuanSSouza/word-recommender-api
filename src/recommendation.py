import numpy as np
import pandas as pd
import nltk
from nltk.corpus import wordnet as wn
import os.path

def calculate_prediction(k, movie, profile, sim_m):
    n = 0
    i = 0
    total = 0

    sim = sim_m.loc[movie][:]
    sim.loc[movie] = 0
    sim = sim.sort_values(ascending=False)
    while n < k and i < len(sim) - 1:
        neig = sim.index[i]
        if neig in profile.index:
            total = total + sim.iloc[i]
            n = n + 1
        i = i + 1

    return total


def generate_rec(number, k, u_row: pd.Series, sim_m: pd.DataFrame):
    profile = u_row[u_row == 1]
    prediction = u_row[u_row == 0]
    for m in prediction.index:
        prediction.loc[m] = calculate_prediction(k, m, profile, sim_m)

    prediction = prediction.sort_values(ascending=False)
    return prediction[:number].tolist(), prediction[:number].index