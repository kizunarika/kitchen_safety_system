from datetime import datetime
import pandas as pd
import serial

from model import KitchenModel
from data_generator import KitchenDataGenerator
from web_interface import KitchenWebInterface
from settings import *


class Main:
    def __init__(self):
        # Load ML model
        self.model = KitchenModel()

        # Serial communication
        # self.ser = serial.Serial(TRANSMISSION_PORT, 115200, timeout=1)

        # Web interface
        self.web = KitchenWebInterface(self)

        # Input source control
        self.input_mode = "web"

        self.time = datetime.now()

    def run(self, cre_df=False, train_model=False):
        # ================= DATA GENERATION =================
        if cre_df:
            print("[INFO] Generate simulation data...")
            KitchenDataGenerator().build_and_save()

        # ================= MODEL =================
        if train_model:
            print("[INFO] Training model...")
            df = pd.read_csv(DF_TRAIN_PATH, parse_dates=["timestamp"])
            self.model.train(df)
        else:
            self.model.load()

        # ================= REAL DATA FILE =================
        try:
            with open(DATA_PATH, "x") as f:
                f.write(
                    "timestamp,"
                    "fire,gas,temp,human,"
                    "stove_on,stove_time,"
                    "gas_delta,temp_delta\n"
                )
        except FileExistsError:
            pass

        # ================= MAIN LOOP =================
        while True:

            if self.input_mode == "serial" and self.ser.in_waiting:
                raw = self.ser.readline().decode().strip().split(" ")

                data = {
                    "fire": int(raw[0]),
                    "gas": float(raw[1]),
                    "temp": float(raw[2]),
                    "human": int(raw[3]),
                    "stove_on": int(raw[4]),
                    "stove_time": float(raw[5]),
                    "gas_delta": float(raw[6]),
                    "temp_delta": float(raw[7])
                }
                self.time = datetime.now()

                print("[INFO] Received from serial:", data)
                self.process_sample(data, source="serial")

    def train_model(self):
        print("[INFO] Training model...")
        df = pd.read_csv(DF_TRAIN_PATH, parse_dates=["timestamp"])
        self.model.train(df)

    # ================= UNIFIED SAMPLE HANDLER =================
    def process_sample(self, feature_dict, source="serial"):
        print("[INFO] Processing sample from", source)
        df = pd.DataFrame([[feature_dict[k]
                          for k in FEATURES]], columns=FEATURES)

        # ---- PREDICT ----
        pred = self.model.model.predict(df)[0]
        print(f"[INFO] Prediction ({source}):", pred)

        # ---- SAVE REAL DATA ----
        self.save_real_data(feature_dict)

        # ---- UPDATE WEB ----
        self.web.update_data(
            prediction=int(pred),
            action=None,
            features=feature_dict
        )

    # ================= SAVE REAL DATA =================
    def save_real_data(self, feature_dict):
        with open(DATA_PATH, "a") as f:
            f.write(
                f"{self.time},"
                f"{feature_dict['fire']},"
                f"{feature_dict['gas']},"
                f"{feature_dict['temp']},"
                f"{feature_dict['human']},"
                f"{feature_dict['stove_on']},"
                f"{feature_dict['stove_time']},"
                f"{feature_dict['gas_delta']},"
                f"{feature_dict['temp_delta']}\n"
            )


if __name__ == "__main__":
    main = Main()
    main.run(cre_df=False, train_model=False)
