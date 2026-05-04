import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, f1_score


class KitchenEvaluator:
    @staticmethod
    def evaluate_and_plot(diag, label_names=None):
        print("\n=== TRAIN REPORT ===\n", diag["classification_report_train"])
        print("\n=== TEST REPORT ===\n", diag["classification_report_test"])

        cm = np.array(diag["confusion_matrix"])
        acc = accuracy_score(diag["y_test"], diag["y_pred"])
        f1 = f1_score(diag["y_test"], diag["y_pred"], average="macro")

        plt.figure(figsize=(6, 5))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=label_names if label_names else np.unique(
                diag["y_test"]),
            yticklabels=label_names if label_names else np.unique(
                diag["y_test"]),
        )
        plt.title(
            f"Confusion Matrix (Test)\nAccuracy={acc:.2f}, F1-macro={f1:.2f}")
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.tight_layout()
        plt.show()

        plt.figure(figsize=(6, 5))
        cm_percent = cm.astype("float") / cm.sum(axis=1, keepdims=True)
        sns.heatmap(
            cm_percent,
            annot=True,
            fmt=".2f",
            cmap="YlGnBu",
            xticklabels=label_names if label_names else np.unique(
                diag["y_test"]),
            yticklabels=label_names if label_names else np.unique(
                diag["y_test"]),
        )
        plt.title("Confusion Matrix (%)")
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.tight_layout()
        plt.show()

        print(f"\nOverall Accuracy: {acc:.3f}")
        print(f"Macro F1-score: {f1:.3f}")
