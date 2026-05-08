from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "waste_model.pkl"
DATASET_PATH = BASE_DIR / "synthetic_waste_dataset.csv"

FEATURES = [
    "plastic_usage",
    "food_delivery_frequency",
    "shopping_frequency",
    "recycling_habits",
    "reusable_item_usage",
]


def generate_dataset(rows=500, seed=42):
    """Create beginner-friendly synthetic data for waste behavior classification."""
    rng = np.random.default_rng(seed)
    data = []

    for _ in range(rows):
        plastic = rng.integers(0, 11)
        delivery = rng.integers(0, 11)
        shopping = rng.integers(0, 11)
        recycling = rng.integers(0, 11)
        reusable = rng.integers(0, 11)

        risk = plastic * 2.5 + delivery * 1.8 + shopping * 1.5 - recycling * 2.0 - reusable * 1.7
        risk += rng.normal(0, 2.5)

        if risk < 8:
            label = "Low Waste"
        elif risk < 22:
            label = "Medium Waste"
        else:
            label = "High Waste"

        data.append([plastic, delivery, shopping, recycling, reusable, label])

    df = pd.DataFrame(data, columns=FEATURES + ["waste_level"])
    df.to_csv(DATASET_PATH, index=False)
    return df


def train_model():
    df = generate_dataset()
    x_train, x_test, y_train, y_test = train_test_split(
        df[FEATURES],
        df["waste_level"],
        test_size=0.2,
        random_state=42,
        stratify=df["waste_level"],
    )

    model = RandomForestClassifier(n_estimators=180, random_state=42, class_weight="balanced")
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)

    joblib.dump({"model": model, "features": FEATURES, "accuracy": accuracy}, MODEL_PATH)
    return accuracy


if __name__ == "__main__":
    print(f"Model trained. Accuracy: {train_model():.2%}")
