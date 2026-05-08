# EcoWise - AI Waste Reduction Recommendation System

EcoWise is a local Flask web application that predicts waste behavior, estimates carbon footprint, explains category probabilities, and recommends sustainable actions.

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

No React, Vite, Node.js, npm, Next.js, Angular, Vue, or npm package manager is required.

## Demo Login

```text
Email: admin@ecowise.local
Password: admin123
```

You can also create a new account from the signup page.

## Project Workflow

1. User signs up or logs in using Flask session authentication.
2. User enters lifestyle habits on the dashboard.
3. Flask sends the values to the Random Forest model.
4. The model predicts `Low Waste`, `Medium Waste`, or `High Waste`.
5. The model returns probability percentages for each category.
6. The app calculates carbon footprint, monthly waste estimate, sustainability score, and future risk.
7. SQLite stores consumption data, predictions, and recommendations.
8. Chart.js visualizes waste composition, weekly trends, and eco improvement.

## Machine Learning Process

The ML model is trained in `ml_model/train_model.py`.

Model:

```text
RandomForestClassifier
```

Features:

- Plastic usage
- Food delivery frequency
- Shopping frequency
- Recycling habits
- Reusable item usage

Labels:

- Low Waste
- Medium Waste
- High Waste

The model is trained from synthetic data because no real dataset is required for the prototype. It saves the trained model as:

```text
ml_model/waste_model.pkl
```

## Probability Prediction Logic

The app uses `predict_proba()` from Scikit-learn to show:

- Chance of Low Waste behavior
- Chance of Medium Waste behavior
- Chance of High Waste behavior

The highest probability becomes the AI confidence score.

## Carbon Footprint Calculation

Formula:

```text
Carbon Footprint Score =
(Plastic Usage x 2.5)
+ (Food Delivery Frequency x 1.8)
+ (Shopping Frequency x 1.5)
- (Recycling Habits x 2.0)
- (Reusable Item Usage x 1.7)
```

Why:

- Plastic increases pollution and landfill load.
- Food delivery adds packaging and transport emissions.
- Shopping frequency increases product packaging.
- Recycling lowers emissions by recovering materials.
- Reusable products reduce repeated single-use waste.

## Database Structure

SQLite database file:

```text
database.db
```

Tables:

- `Users`
- `ConsumptionData`
- `WastePredictions`
- `Recommendations`

The database is initialized automatically when `python app.py` starts.

## Frontend

Uses only:

- HTML templates
- CSS
- Vanilla JavaScript
- Bootstrap 5 CDN
- Bootstrap Icons CDN
- Chart.js CDN

Pages:

- `templates/index.html`
- `templates/login.html`
- `templates/signup.html`
- `templates/dashboard.html`
- `templates/admin.html`
