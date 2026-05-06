DELTA_TIMESTAMP = 3  # seconds
N_SAMPLES = 800
TRANSMISSION_PORT = 'COM6'
MODEL_PATH = "kitchen_model.pkl"
DF_TRAIN_PATH = "df_train.csv"
DATA_PATH = "static/kitchen_data.csv"
RULES_PATH = "static/kitchen_rules.csv"


FEATURES = [
    "fire",
    "gas",
    "temp",
    "human",
    "stove_on",
    "stove_time",
    "gas_delta",
    "temp_delta"
]

LABEL_COL = "label"


# ================= THRESHOLD CONFIG =================

TH_FIRE_WEIGHT = (3.2, 4.0)

TH_GAS_NORM = 200
TH_GAS_DANGER = 400
TH_GAS_SCALE = 400
TH_GAS_WEIGHT = (1.0, 1.3)

TH_TEMP_NORM = 40
TH_TEMP_DANGER = 60
TH_TEMP_SCALE = 55
TH_TEMP_WEIGHT = (1.0, 1.3)

TH_STOVE_TIME_SCALE = 600  # giây
TH_STOVE_TIME_WEIGHT = (1.0, 1.4)

TH_GAS_DELTA_SCALE = (90, 140)
TH_TEMP_DELTA_SCALE = (6, 10)

TH_RANDOM_NOISE = (-0.4, 0.4)

TH_LABEL_WARN = 3.5
TH_LABEL_DANGER = 6.8
