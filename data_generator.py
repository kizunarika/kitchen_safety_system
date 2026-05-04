import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta
from settings import *


class KitchenDataGenerator:
    def __init__(
        self,
        n_samples=N_SAMPLES,
        interval_seconds=DELTA_TIMESTAMP,
        noise_level=0.1,
        start_time=None
    ):
        self.n_samples = n_samples
        self.interval_seconds = interval_seconds
        self.noise_level = noise_level
        self.start_time = start_time or datetime.now()

    # ================= SOFT LABEL =================
    def _soft_label(self, row):
        score = 0.0

        score += row["fire"] * random.uniform(*TH_FIRE_WEIGHT)

        score += (row["gas"] / TH_GAS_SCALE) * random.uniform(*TH_GAS_WEIGHT)

        score += (row["temp"] / TH_TEMP_SCALE) * \
            random.uniform(*TH_TEMP_WEIGHT)

        if row["stove_on"] == 1 and row["human"] == 0:
            score += (row["stove_time"] / TH_STOVE_TIME_SCALE) * \
                random.uniform(*TH_STOVE_TIME_WEIGHT)

        score += max(0, row["gas_delta"]) / random.uniform(*TH_GAS_DELTA_SCALE)
        score += max(0, row["temp_delta"]) / \
            random.uniform(*TH_TEMP_DELTA_SCALE)

        score += random.uniform(*TH_RANDOM_NOISE)

        if score >= TH_LABEL_DANGER:
            return 2
        elif score >= TH_LABEL_WARN:
            return 1
        return 0

    # ================= GENERATE RAW DATA =================

    def generate(self):
        rows = []

        gas = random.uniform(90, 130)
        temp = random.uniform(26, 34)
        stove_time = 0

        prev_gas, prev_temp = gas, temp
        timestamp = self.start_time

        for _ in range(self.n_samples):

            env = random.choices(
                ["normal", "unstable", "critical"],
                weights=[0.55, 0.30, 0.15]
            )[0]

            fire = 1 if env == "critical" and random.random() < 0.25 else 0
            stove_on = random.choice([0, 1])
            human = random.choice([0, 1])

            if env == "normal":
                gas += random.uniform(-6, 10)
                temp += random.uniform(-0.6, 0.7)
            elif env == "unstable":
                gas += random.uniform(6, 40)
                temp += random.uniform(1.0, 3.2)
            else:
                gas += random.uniform(25, 110)
                temp += random.uniform(3.0, 8.5)

            if random.random() < 0.18:
                gas += random.uniform(-35, 35)
                temp += random.uniform(-4, 4)

            if stove_on:
                stove_time += self.interval_seconds
            else:
                stove_time = 0

            gas *= np.random.normal(1, self.noise_level)
            temp *= np.random.normal(1, self.noise_level)

            gas = max(0, gas)
            temp = max(0, temp)

            gas_delta = gas - prev_gas
            temp_delta = temp - prev_temp

            row = {
                "timestamp": timestamp,
                "fire": fire,
                "gas": round(gas, 2),
                "temp": round(temp, 2),
                "human": human,
                "stove_on": stove_on,
                "stove_time": round(stove_time, 2),
                "gas_delta": round(gas_delta, 2),
                "temp_delta": round(temp_delta, 2),
            }

            row["label"] = self._soft_label(row)
            rows.append(row)

            prev_gas, prev_temp = gas, temp
            timestamp += timedelta(seconds=self.interval_seconds)

        return pd.DataFrame(rows)

    # ================= BALANCE, SAVE =================
    def build_and_save(self, path=DF_TRAIN_PATH):
        df = self.generate()

        parts = []

        count_0 = max(len(df[df["label"] == 0]), 500)
        count_1 = max(len(df[df["label"] == 1]), 500)
        target_2 = int((count_0 + count_1) * 1.2)

        parts.append(df[df["label"] == 0].sample(
            count_0, replace=True, random_state=42))
        parts.append(df[df["label"] == 1].sample(
            count_1, replace=True, random_state=42))
        parts.append(df[df["label"] == 2].sample(
            min(len(df[df["label"] == 2]), target_2),
            random_state=42
        ))

        df_final = (
            pd.concat(parts)
            .sample(frac=1, random_state=42)
            .reset_index(drop=True)
        )

        df_final.to_csv(path, index=False)

        print("[INFO] Saved generated data to:", path)
        print(df_final["label"].value_counts())

        return df_final
