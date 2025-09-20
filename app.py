import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import requests
import json
from firebase_admin import credentials, initialize_app, db
import firebase_admin

# ---------------- Streamlit Config ---------------- #
st.set_page_config(page_title="Smart Dewatering Prototype", layout="wide")
st.title("🚰 Smart Dewatering Dashboard (IoT + AI + Solar)")

# ---------------- Firebase Setup ---------------- #
# Load Firebase secrets from Streamlit Cloud (Secrets Manager)
if not firebase_admin._apps:
    sa_json = json.loads(st.secrets["FIREBASE_SERVICE_ACCOUNT"])
    cred = credentials.Certificate(sa_json)
    initialize_app(cred, {"databaseURL": st.secrets["FIREBASE_DB_URL"]})

ref = db.reference("sensor_data")
data = ref.get() or {}

rain = data.get("rainfall", 10)           # mm
water_level = data.get("water_level", 30) # %
pump_current = data.get("pump_current", 10) # A

# ---------------- Display Live Sensor Data ---------------- #
st.header("🌐 Live Sensor Data (from Proteus)")
col1, col2, col3 = st.columns(3)
col1.metric("🌧 Rainfall (mm)", rain)
col2.metric("💧 Water Level (%)", water_level)
col3.metric("⚡ Pump Current (A)", pump_current)

# ---------------- AI/ML Model: Water Inflow Prediction ---------------- #
st.header("1️⃣ Water Inflow Prediction")

# Dummy dataset for training
df = pd.DataFrame({
    "Rain_mm": [0, 10, 20, 30, 40, 50],
    "Water_Inflow": [10, 100, 220, 350, 480, 600]
})
X, y = df[["Rain_mm"]], df["Water_Inflow"]
model = LinearRegression().fit(X, y)

pred_inflow = model.predict([[rain]])[0]
st.success(f"💧 Predicted Water Inflow: {pred_inflow:.2f} liters")

# ---------------- Pump Scheduling ---------------- #
st.header("2️⃣ Pump Scheduling Optimization")

solar_capacity, grid_capacity, diesel_capacity = 200, 150, 300
if pred_inflow <= solar_capacity:
    decision = "✅ Use Solar Only"
elif pred_inflow <= solar_capacity + grid_capacity:
    decision = "⚡ Use Solar + Grid"
else:
    decision = "🚨 Use Solar + Grid + Diesel"

st.info(f"AI Decision: {decision}")

# ---------------- Predictive Maintenance ---------------- #
st.header("3️⃣ Predictive Maintenance Check")

pump_data = [10, 11, 9, 10, pump_current, 11, 10]
mean, std = np.mean(pump_data), np.std(pump_data)
if abs(pump_current - mean) > 2 * std:
    st.error(f"⚠ Anomaly Detected in Pump Current: {pump_current} A")
else:
    st.success("✅ Pump running normally")

# ---------------- Billing ---------------- #
st.header("4️⃣ Billing & Analytics")

rate = 0.5  # Rs. per liter
bill = pred_inflow * rate
st.write(f"💵 Bill = ₹{bill:.2f}")

# ---------------- Carbon Credits ---------------- #
st.header("5️⃣ Carbon Credit Tracking")

diesel_saved = 20  # liters (dummy value)
emission_factor = 2.68  # kg CO₂ per liter diesel
co2_saved = diesel_saved * emission_factor

st.write(f"🌍 Estimated CO₂ Savings: {co2_saved:.2f} kg")
st.write(f"💰 Equivalent Diesel Saved: {diesel_saved} liters")
st.secrets["FIREBASE"]["FIREBASE_SERVICE_ACCOUNT"]


