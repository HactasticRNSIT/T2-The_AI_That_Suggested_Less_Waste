from pathlib import Path

import joblib
import pandas as pd

from ml_model.train_model import FEATURES, MODEL_PATH, train_model


def load_model():
    if not MODEL_PATH.exists():
        train_model()
    return joblib.load(MODEL_PATH)


def calculate_carbon_footprint(plastic, delivery, shopping, recycling, reusable):
    """Formula requested in the project spec."""
    score = (plastic * 2.5) + (delivery * 1.8) + (shopping * 1.5) - (recycling * 2.0) - (reusable * 1.7)
    return max(0, round(score, 2))


def make_prediction(payload):
    bundle = load_model()
    model = bundle["model"]
    row = {
        "plastic_usage": float(payload.get("plastic_usage", 0)),
        "food_delivery_frequency": float(payload.get("food_delivery_frequency", 0)),
        "shopping_frequency": float(payload.get("shopping_frequency", 0)),
        "recycling_habits": float(payload.get("recycling_habits", 0)),
        "reusable_item_usage": float(payload.get("reusable_item_usage", 0)),
    }

    frame = pd.DataFrame([row], columns=FEATURES)
    waste_level = model.predict(frame)[0]
    probabilities = dict(zip(model.classes_, model.predict_proba(frame)[0]))

    carbon = calculate_carbon_footprint(
        row["plastic_usage"],
        row["food_delivery_frequency"],
        row["shopping_frequency"],
        row["recycling_habits"],
        row["reusable_item_usage"],
    )
    waste_score = min(100, round(carbon * 3.2 + row["plastic_usage"] * 2 + row["food_delivery_frequency"] * 1.5))
    monthly_waste_estimate = round((waste_score / 100) * 42 + row["shopping_frequency"] * 0.8, 2)
    sustainability_score = max(0, round(100 - waste_score + row["recycling_habits"] + row["reusable_item_usage"]))
    confidence = round(max(probabilities.values()) * 100, 1)

    return {
        "waste_level": waste_level,
        "waste_score": waste_score,
        "carbon_footprint": carbon,
        "monthly_waste_estimate": monthly_waste_estimate,
        "sustainability_score": sustainability_score,
        "probability_low": round(probabilities.get("Low Waste", 0) * 100, 1),
        "probability_medium": round(probabilities.get("Medium Waste", 0) * 100, 1),
        "probability_high": round(probabilities.get("High Waste", 0) * 100, 1),
        "confidence": confidence,
        "certainty": "High" if confidence >= 70 else "Medium" if confidence >= 50 else "Low",
        "future_risk": future_risk_text(row, probabilities.get("High Waste", 0) * 100),
        "recommendations": generate_recommendations(row, waste_level, carbon, probabilities.get("High Waste", 0) * 100),
        "composition": waste_composition(row),
        "weekly": weekly_series(waste_score, carbon),
        "risk_factors": risk_factors(row),
    }


def risk_factors(row):
    factors = []
    if row["plastic_usage"] >= 6:
        factors.append("High plastic usage strongly increases pollution and High Waste probability.")
    if row["food_delivery_frequency"] >= 5:
        factors.append("Frequent food delivery adds packaging waste and transport emissions.")
    if row["shopping_frequency"] >= 6:
        factors.append("Frequent shopping increases packaging and product disposal risk.")
    if row["recycling_habits"] <= 4:
        factors.append("Low recycling habits reduce waste recovery and increase landfill impact.")
    if row["reusable_item_usage"] <= 4:
        factors.append("Low reusable item usage increases disposable product dependency.")
    return factors or ["Your current habits show balanced environmental risk."]


def generate_recommendations(row, waste_level, carbon, high_probability):
    tips = []
    if row["plastic_usage"] >= 4:
        tips.append(("Reduce plastic bottle usage and use reusable bottles.", "Plastic"))
    if row["food_delivery_frequency"] >= 4:
        tips.append(("Reduce food delivery frequency or choose low-packaging restaurants.", "Food Packaging"))
    if row["shopping_frequency"] >= 4:
        tips.append(("Buy refill packs and avoid over-packaged products.", "Shopping"))
    if row["recycling_habits"] <= 5:
        tips.append(("Recycle more frequently and separate dry/wet waste.", "Recycling"))
    if row["reusable_item_usage"] <= 5:
        tips.append(("Carry cloth bags, reusable cups, and steel bottles.", "Reusable"))
    if carbon > 20 or high_probability > 45 or waste_level == "High Waste":
        tips.append(("Set a weekly low-waste challenge to reduce future pollution risk.", "Action Plan"))
    return tips or [("Excellent pattern. Maintain your low-waste routine.", "Maintenance")]


def future_risk_text(row, high_probability):
    increase = min(30, round(row["plastic_usage"] * 1.2 + row["food_delivery_frequency"] * 0.9, 1))
    if high_probability >= 45:
        return f"If plastic and delivery habits continue, High Waste probability may increase by {increase}% next month."
    return "Current habits show manageable future risk if recycling and reusable item usage continue."


def waste_composition(row):
    plastic = row["plastic_usage"] * 3.5
    food_packaging = row["food_delivery_frequency"] * 2.8
    food_waste = row["food_delivery_frequency"] * 1.6
    recyclable = max(1, row["recycling_habits"] * 1.4)
    reusable_savings = max(1, row["reusable_item_usage"] * 1.7)
    total = plastic + food_packaging + food_waste + recyclable + reusable_savings

    def part(value):
        pct = round((value / total) * 100, 1)
        amount = round((value / total) * 18, 2)
        return {"percentage": pct, "amount": amount}

    return {
        "Plastic Waste": part(plastic),
        "Food Packaging Waste": part(food_packaging),
        "Food Waste": part(food_waste),
        "Recyclable Waste": part(recyclable),
        "Reusable Savings": part(reusable_savings),
    }


def weekly_series(waste_score, carbon):
    return {
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "waste": [max(0, waste_score + delta) for delta in [-8, -4, 0, 4, 6, 2, -3]],
        "carbon": [max(0, round(carbon + delta, 1)) for delta in [-3, -1.5, -0.5, 1, 2, 0.5, -1]],
        "recycling": [42, 48, 50, 55, 59, 63, 68],
        "plastic": [66, 63, 60, 58, 55, 52, 49],
        "eco": [50, 54, 58, 63, 67, 72, 78],
    }
