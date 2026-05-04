import joblib
import os
from settings import *
from sklearn.ensemble import RandomForestClassifier


class KitchenModel:
    def __init__(self, random_state=42):
        self.features = FEATURES
        self.label_col = LABEL_COL
        self.model_path = MODEL_PATH
        self.random_state = random_state
        self.model = None

    # ================= BUILD MODEL =================
    def _build_model(self):
        return RandomForestClassifier(
            n_estimators=300,
            max_depth=14,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=self.random_state,
            n_jobs=-1
        )

    # ================= TRAIN =================
    def train(self, df):
        df = df.copy()

        if "timestamp" in df.columns:
            df.drop(columns=["timestamp"], inplace=True)

        for col in self.features + [self.label_col]:
            if col not in df.columns:
                raise ValueError(f"[ERROR] Missing column: {col}")

        x = df[self.features].astype(float)
        y = df[self.label_col].astype(int)

        self.model = self._build_model()
        self.model.fit(x, y)
        self.save(self.model_path)

        return self.model

    # ================= LOAD =================
    def load(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                "[ERROR] The model does not exist. Please train the model first.")

        self.model = joblib.load(self.model_path)

        return self.model

    def save(self, path):
        if self.model is None:
            raise ValueError("[ERROR] No model to save.")

        joblib.dump(
            self.model,
            path
        )
