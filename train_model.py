"""
IPL Ticket Price Predictor — Model Training Script
====================================================
Trains and evaluates multiple regression models, selects the best one
based on R² score, and saves it as model.pkl.

Run: python train_model.py
"""

import pandas as pd
import numpy as np
import pickle
import joblib
import os
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ──────────────────────────────────────────────────────────────────────────────
# 1. LOAD DATASET
# ──────────────────────────────────────────────────────────────────────────────
print("=" * 60)
print("  IPL Ticket Price Predictor — Model Training")
print("=" * 60)

df = pd.read_csv("dataset/ipl_ticket_dataset.csv")
print(f"\n[INFO] Dataset loaded: {df.shape[0]} rows × {df.shape[1]} columns")

# ──────────────────────────────────────────────────────────────────────────────
# 2. DATA CLEANING
# ──────────────────────────────────────────────────────────────────────────────
print("\n[INFO] Checking for missing values...")
print(df.isnull().sum())
df.dropna(inplace=True)
print(f"[INFO] Records after cleaning: {len(df)}")

# ──────────────────────────────────────────────────────────────────────────────
# 3. FEATURE ENGINEERING
# ──────────────────────────────────────────────────────────────────────────────
print("\n[INFO] Encoding categorical features...")

# Drop non-predictive columns
drop_cols = ["Match_Date", "Base_Price"]
df.drop(columns=drop_cols, inplace=True)

# Label encode all categorical columns
categorical_cols = [
    "Match_Day", "Match_Time", "Stadium", "City",
    "Home_Team", "Away_Team", "Stand_Type", "Seat_Category",
    "Match_Type", "Weekend", "Holiday", "Opponent_Popularity",
    "Weather", "Demand_Level", "Booking_Time"
]

encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    encoders[col] = le
    print(f"   Encoded: {col} ({len(le.classes_)} classes)")

# Save encoders
os.makedirs("model_artifacts", exist_ok=True)
with open("model_artifacts/encoders.pkl", "wb") as f:
    pickle.dump(encoders, f)
print("[INFO] Encoders saved to model_artifacts/encoders.pkl")

# ──────────────────────────────────────────────────────────────────────────────
# 4. TRAIN-TEST SPLIT
# ──────────────────────────────────────────────────────────────────────────────
X = df.drop(columns=["Predicted_Price"])
y = df["Predicted_Price"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\n[INFO] Train size: {X_train.shape[0]} | Test size: {X_test.shape[0]}")

# Save feature column names
feature_columns = list(X.columns)
with open("model_artifacts/feature_columns.pkl", "wb") as f:
    pickle.dump(feature_columns, f)
print(f"[INFO] Feature columns saved: {feature_columns}")

# ──────────────────────────────────────────────────────────────────────────────
# 5. DEFINE MODELS
# ──────────────────────────────────────────────────────────────────────────────
models = {
    "Linear Regression":       LinearRegression(),
    "Decision Tree Regressor": DecisionTreeRegressor(random_state=42, max_depth=12),
    "Random Forest Regressor": RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1),
    "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=200, random_state=42)
}

# ──────────────────────────────────────────────────────────────────────────────
# 6. TRAIN & EVALUATE
# ──────────────────────────────────────────────────────────────────────────────
results = {}
print("\n" + "=" * 60)
print("  Model Evaluation Results")
print("=" * 60)

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mae  = mean_absolute_error(y_test, y_pred)
    mse  = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2   = r2_score(y_test, y_pred)

    results[name] = {"model": model, "MAE": mae, "MSE": mse, "RMSE": rmse, "R2": r2}

    print(f"\n  Model  : {name}")
    print(f"  MAE    : ₹{mae:,.2f}")
    print(f"  MSE    : {mse:,.2f}")
    print(f"  RMSE   : ₹{rmse:,.2f}")
    print(f"  R² Score: {r2:.4f}")
    print("  " + "-" * 40)

# ──────────────────────────────────────────────────────────────────────────────
# 7. SELECT BEST MODEL
# ──────────────────────────────────────────────────────────────────────────────
best_name = max(results, key=lambda k: results[k]["R2"])
best_model = results[best_name]["model"]
best_r2    = results[best_name]["R2"]

print(f"\n{'=' * 60}")
print(f"  BEST MODEL: {best_name}")
print(f"  R² Score  : {best_r2:.4f}")
print(f"{'=' * 60}")

# ──────────────────────────────────────────────────────────────────────────────
# 8. SAVE MODEL
# ──────────────────────────────────────────────────────────────────────────────
with open("model.pkl", "wb") as f:
    pickle.dump(best_model, f)
print("\n[INFO] Best model saved as model.pkl")

# Also save with joblib for redundancy
joblib.dump(best_model, "model_artifacts/model_joblib.pkl")
print("[INFO] Redundant copy saved via joblib at model_artifacts/model_joblib.pkl")

print("\n[SUCCESS] Training complete. Run `python application.py` to start the Flask app.")
