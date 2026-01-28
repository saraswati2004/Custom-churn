import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Churn Prediction App", layout="centered")
st.title("📉 Customer Churn Prediction (JWT Secured)")

# ---------------- SESSION ----------------
if "token" not in st.session_state:
    st.session_state.token = None

# ================= AUTH SECTION =================
st.subheader("🔐 Authentication")

tab1, tab2 = st.tabs(["Register", "Login"])

# ---------- REGISTER ----------
with tab1:
    r_user = st.text_input("Username", key="r_user")
    r_pass = st.text_input("Password", type="password", key="r_pass")

    if st.button("Register"):
        res = requests.post(
            f"{BASE_URL}/register",
            json={"username": r_user, "password": r_pass}
        )

        if res.status_code == 200:
            st.success("Registered successfully 🎉")
            st.session_state.token = res.json()["access_token"]
        else:
            st.error(res.json().get("detail"))

# ---------- LOGIN ----------
with tab2:
    l_user = st.text_input("Username", key="l_user")
    l_pass = st.text_input("Password", type="password", key="l_pass")

    if st.button("Login"):
        res = requests.post(
            f"{BASE_URL}/login",
            json={"username": l_user, "password": l_pass}
        )

        if res.status_code == 200:
            st.success("Login successful ✅")
            st.session_state.token = res.json()["access_token"]
        else:
            st.error("Invalid username or password")

# ================= PREDICTION =================
st.divider()
st.subheader("🔮 Predict Customer Churn")

if st.session_state.token is None:
    st.warning("Please login to access prediction")
else:
    st.success("Authenticated ✔️")

    with st.form("prediction_form"):
        Gender = st.selectbox("Gender", ["Male", "Female"])
        Age = st.number_input("Age", 18, 100, 30)
        Tenure = st.number_input("Tenure", 0, 100, 12)
        Services_Subscribed = st.number_input("Services Subscribed", 0, 10, 2)
        Contract_Type = st.selectbox(
            "Contract Type",
            ["Month-to-month", "One year", "Two year"]
        )
        MonthlyCharges = st.number_input("Monthly Charges", 1.0)
        TotalCharges = st.number_input("Total Charges", 0.0)
        TechSupport = st.selectbox("Tech Support", ["yes", "no"])
        OnlineSecurity = st.selectbox("Online Security", ["yes", "no"])
        InternetService = st.selectbox(
            "Internet Service",
            ["DSL", "Fiber optic", "No"]
        )

        submit = st.form_submit_button("Predict")

    if submit:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        payload = {
            "customer": {
                "Gender": Gender,
                "Age": Age,
                "Tenure": Tenure,
                "Services_Subscribed": Services_Subscribed,
                "Contract_Type": Contract_Type,
                "MonthlyCharges": MonthlyCharges,
                "TotalCharges": TotalCharges,
                "TechSupport": TechSupport,
                "OnlineSecurity": OnlineSecurity,
                "InternetService": InternetService
            }
        }

        res = requests.post(
            f"{BASE_URL}/predict/auth",
            json=payload,
            headers=headers
        )

        if res.status_code == 200:
            result = res.json()

            st.success("Prediction Successful 🎯")
            st.metric("Churn Status", result["Churn_label"])

            if result.get("Churn_probability") is not None:
                st.metric(
                    "Churn Probability",
                    f"{result['Churn_probability']*100:.2f}%"
                )
        else:
            try:
                st.error(res.json().get("detail", res.text))
            except ValueError:
                st.error(res.text)
