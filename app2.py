from datetime import datetime
import serial
from web_interface import KitchenWebInterface
from settings import *
import os


class Main:
    def __init__(self):
        # Serial communication
        self.ser = serial.Serial(TRANSMISSION_PORT, 115200, timeout=1)

        # Web interface
        self.web = KitchenWebInterface(self)

        # Input source control
        self.input_mode = "serial"

        self.time = datetime.now()

        self.rules = self.load_rules(RULES_PATH)

    def run(self):
        while True:
            if self.input_mode == "serial" and self.ser.in_waiting:
                raw_line = self.ser.readline().decode(errors="ignore").strip()
                # print("[RAW]", raw_line)
                if not raw_line:
                    continue
                raw = raw_line.split(",")
                if len(raw) != 9:
                    print("[WARN] Sai format:", raw_line)
                    continue

                data = {
                    "fire": int(raw[0]),
                    "gas": float(raw[1]),
                    "temp": float(raw[2]),
                    "human": int(raw[3]),
                    "stove_on": int(raw[4]),
                    "absence_time": float(raw[5]),
                    "stove_time": float(raw[6]),
                    "gas_delta": float(raw[7]),
                    "temp_delta": float(raw[8]),
                    # "prediction": int(raw[9])
                }
                self.time = datetime.now()

                print("[INFO] Received from serial:", data)
                self.process_sample(data, source="serial")

    def process_sample(self, data, source="serial"):
        print("[INFO] Processing sample from", source)

        # ---- PREDICT ----
        pred = self.predict(data)
        print(f"[INFO] Prediction ({source}):", pred)
        data["prediction"] = int(pred)

        # ---- SEND ARDUINO ----
        try:
            self.ser.write((str(pred) + "\n").encode())
            self.ser.flush()
        except Exception as e:
            print("[ERROR] Send fail:", e)

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
                f"{data['absence_time']},"
                f"{data['stove_time']},"
                f"{data['gas_delta']},"
                f"{data['temp_delta']},"
                f"{data['prediction']}\n"
            )

    def predict(self, data):
        # ===== CUSTOM RULES =====
        for cond, result in self.rules:
            try:
                if eval(cond, {"__builtins__": None}, data):
                    return result
            except Exception as e:
                print("[RULE ERROR]", cond, e)

        # ===== 🚨 DANGER =====

        # Có lửa + nhiệt quá cao → cháy
        if data["fire"] == 1 and data["temp"] > 55:
            return 2

        # Bếp bật nhưng không có lửa sau 10s → xì gas cực nguy hiểm
        if data["stove_on"] == 1 and data["fire"] == 0 and data["stove_time"] > 10:
            return 2

        # Gas rất cao và không có lửa → rò gas
        if data["gas"] > 750 and data["fire"] == 0:
            return 2

        # Không có người + bếp bật lâu → nguy hiểm
        if data["stove_on"] == 1 and data["absence_time"] > 120:
            return 2

        # Gas tăng + không có người
        if data["gas"] > 600 and data["human"] == 0:
            return 2

        # ===== ⚠️ WARNING =====

        # Có lửa + gas cao vừa → bất thường
        if data["fire"] == 1 and data["gas"] > 600:
            return 1

        # Nhiệt + gas cùng tăng
        if data["temp"] > 45 and data["gas"] > 500:
            return 1

        # Không có người nhưng chưa quá lâu
        if data["stove_on"] == 1 and data["human"] == 0 and data["absence_time"] > 30:
            return 1

        # Nấu quá lâu (có người)
        if data["human"] == 1 and data["stove_time"] > 900:
            return 1

        # Gas hơi cao nhưng chưa nguy hiểm
        if data["gas"] > 400 and data["fire"] == 0:
            return 1

        # ===== ✅ SAFE =====
        return 0

    def load_rules(self, file_path):
        if not os.path.exists(file_path):
            print("[WARN] Không tìm thấy file rule")
            return []

        rules = []
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                try:
                    cond, result = line.rsplit(",", 1)

                    cond = cond.strip()
                    result = int(result.strip())

                    rules.append((cond, result))

                except Exception as e:
                    print("[ERROR] Rule sai:", line, "|", e)

        return rules


if __name__ == "__main__":
    main = Main()
    main.run()
