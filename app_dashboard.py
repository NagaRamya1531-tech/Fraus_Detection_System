import streamlit as st
import pandas as pd
import numpy as np
import pickle
import time
from twilio.rest import Client

from dotenv import load_dotenv
import os

load_dotenv()  # Load from .env

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
TWILIO_WHATSAPP_TO = os.getenv("TWILIO_WHATSAPP_TO")


# -----------------------------
# WhatsApp Alert Function
# -----------------------------
def send_whatsapp_alert(probability):
    """Send WhatsApp alert when fraud detected with high probability."""
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH)
        message = client.messages.create(
            body=f"🚨 Fraud Alert: Transaction flagged with {probability:.2%} probability!",
            from_=TWILIO_WHATSAPP_FROM,
            to=TWILIO_WHATSAPP_TO
        )
        print("✅ WhatsApp alert sent:", message.sid)
        st.toast("📲 WhatsApp alert sent successfully!", icon="✅")
    except Exception as e:
        print("WhatsApp sending failed:", e)
        st.warning("⚠️ WhatsApp alert could not be sent.")

# -----------------------------
# Load trained model
# -----------------------------
MODEL_PATH = "fraud_model.pkl"
with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)

# Load test dataset for demo simulation (optional)
try:
    X_test = pd.read_csv("data/X_test.csv")
except:
    X_test = None

# Map transaction types (must match model encoding)
type_map = {
    "CASH-IN": 0,
    "CASH-OUT": 1,
    "DEBIT": 2,
    "PAYMENT": 3,
    "TRANSFER": 4
}

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Fraud Detection Dashboard", layout="wide")
st.title("🏦 Real-Time Fraud Detection System")
st.write("This app predicts whether a transaction is fraudulent using a trained machine learning model and sends real-time WhatsApp alerts.")

# Example input table
st.markdown("### 📌 Example Transaction Input")
example_data = {
    "step": [100],
    "type": ["TRANSFER"],
    "amount": [25000.50],
    "oldbalanceOrg": [30000.00],
    "newbalanceOrig": [5000.00],
    "oldbalanceDest": [1000.00],
    "newbalanceDest": [26000.50]
}
st.table(pd.DataFrame(example_data))

# Prediction legend
st.markdown("**Prediction Legend:** `0` = Legitimate ✅ | `1` = Fraudulent 🚨")
st.markdown("---")

# -----------------------------
# Sidebar input form
# -----------------------------
st.sidebar.header("🔹 Enter Transaction Details")
step = st.sidebar.number_input("Step (1-744)", min_value=1, max_value=744, value=100)
trans_type = st.sidebar.selectbox("Transaction Type", list(type_map.keys()))
amount = st.sidebar.number_input("Transaction Amount", min_value=0.0, value=1000.0, step=100.0)
oldbalanceOrg = st.sidebar.number_input("Old Balance (Sender)", min_value=0.0, value=5000.0, step=100.0)
newbalanceOrig = st.sidebar.number_input("New Balance (Sender)", min_value=0.0, value=4000.0, step=100.0)
oldbalanceDest = st.sidebar.number_input("Old Balance (Receiver)", min_value=0.0, value=1000.0, step=100.0)
newbalanceDest = st.sidebar.number_input("New Balance (Receiver)", min_value=0.0, value=2000.0, step=100.0)

# Prepare input
features = np.array([[step, type_map[trans_type], amount, oldbalanceOrg, newbalanceOrig, oldbalanceDest, newbalanceDest]])

# Prediction button
if st.sidebar.button("🚨 Predict Fraud"):
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0][1]

    st.subheader("🔍 Prediction Result")
    if prediction == 1:
        st.error(f"🚨 Fraudulent Transaction Detected! (Probability: {probability:.2%})")
        if probability > 0.90:
            send_whatsapp_alert(probability)
    else:
        st.success(f"✅ Legitimate Transaction (Fraud Probability: {probability:.2%})")

# -----------------------------
# Random Transaction Simulation
# -----------------------------
st.markdown("---")
st.subheader("🎲 Simulate Random Predictions")

if X_test is not None:
    if st.button("Generate Predictions for 5 Random Transactions"):
        sample_df = X_test.sample(5, random_state=None)
        preds = model.predict(sample_df)
        probs = model.predict_proba(sample_df)[:, 1]

        result = sample_df.copy()
        result['Fraud_Prediction'] = preds
        result['Fraud_Probability'] = probs.round(6)
        st.write(result)

        fraud_count = (preds == 1).sum()
        st.metric("🚨 Fraudulent Transactions Detected", fraud_count)
else:
    st.info("Random transaction simulation unavailable (missing X_test.csv).")

# -----------------------------
# Live Transaction Feed Simulation with Stop Button
# -----------------------------
st.markdown("---")
st.subheader("🔴 Live Transaction Feed Simulation")

# Initialize session state for controlling simulation
if "run_simulation" not in st.session_state:
    st.session_state.run_simulation = False

col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ Start Live Simulation"):
        st.session_state.run_simulation = True

with col2:
    if st.button("⏹ Stop Simulation"):
        st.session_state.run_simulation = False
        st.info("✅ Simulation stopped manually.")

if X_test is not None and st.session_state.run_simulation:
    placeholder = st.empty()
    for i in range(100):  # simulate up to 100 transactions
        if not st.session_state.run_simulation:
            break  # exit loop if Stop button is pressed

        sample = X_test.sample(1)
        pred = model.predict(sample)[0]
        prob = model.predict_proba(sample)[0][1]

        with placeholder.container():
            st.write("**Incoming Transaction:**")
            st.dataframe(sample)
            if pred == 1:
                st.error(f"🚨 FRAUD ALERT! Probability: {prob:.2%}")
                if prob > 0.90:
                    send_whatsapp_alert(prob)
            else:
                st.success(f"✅ Legitimate Transaction (Fraud Probability: {prob:.2%})")

        time.sleep(2)
else:
    st.info("Click ▶️ Start Live Simulation to begin streaming transactions.")
