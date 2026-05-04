from datetime import datetime
import serial
from web_interface import KitchenWebInterface
from settings import *


class Main:
    def __init__(self):
        # Serial communication
        self.ser = serial.Serial(TRANSMISSION_PORT, 115200, timeout=1)

        # Web interface
        self.web = KitchenWebInterface(self)

        # Input source control
        self.input_mode = "serial"

        self.time = datetime.now()

    def run(self):
        while True:
            if self.input_mode == "serial" and self.ser.in_waiting:
                raw_line = self.ser.readline().decode(errors="ignore").strip()
                print("[RAW]", raw_line)
                if not raw_line:
                    return
                raw = raw_line.split(",")
                if len(raw) != 9:
                    print("[WARN] Sai format:", raw_line)
                    return

                data = {
                    "fire": int(raw[0]),
                    "gas": float(raw[1]),
                    "temp": float(raw[2]),
                    "human": int(raw[3]),
                    "stove_on": int(raw[4]),
                    "absent_time": float(raw[5]),
                    "gas_delta": float(raw[6]),
                    "temp_delta": float(raw[7]),
                    "prediction": int(raw[8])
                }
                self.time = datetime.now()

                print("[INFO] Received from serial:", data)
                self.process_sample(data, source="serial")

    def process_sample(self, data, source="serial"):
        print("[INFO] Processing sample from", source)

        # ---- PREDICT ----
        pred = data["prediction"]
        print(f"[INFO] Prediction ({source}):", pred)

        # ---- SAVE REAL DATA ----
        self.save_real_data(data)

        # ---- UPDATE WEB ----
        self.web.update_data(
            prediction=int(pred),
            action=None,
            features=data
        )

    def save_real_data(self, data):
        with open(DATA_PATH, "a") as f:
            f.write(
                f"{self.time},"
                f"{data['fire']},"
                f"{data['gas']},"
                f"{data['temp']},"
                f"{data['human']},"
                f"{data['stove_on']},"
                f"{data['absent_time']},"
                f"{data['gas_delta']},"
                f"{data['temp_delta']},"
                f"{data['prediction']}\n"
            )


if __name__ == "__main__":
    main = Main()
    main.run()
