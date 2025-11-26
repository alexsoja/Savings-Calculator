# --- Test Application

# -- Imports
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Session State Initialization ---
if "df" not in st.session_state:
    st.session_state.df = None

if "yearly_df" not in st.session_state:
    st.session_state.yearly_df = None

# -- Page Layout
st.title("💰 Savings Growth Predictor")
st.sidebar.title("Navigation")
options = st.sidebar.radio("Pages", options=["Data Statistics","Data Visualizations"])

# -- Data Collection
balance = st.sidebar.number_input("Enter Current Balance:", min_value=0.0)
apy = st.sidebar.number_input("Enter APY (as decimal, e.g. 0.04 for 4%):", min_value=0.0, max_value=1.0,format="%.4f")
monthly_deposit = st.sidebar.number_input("Enter Monthly Deposit:", min_value=0.0)
months = st.sidebar.number_input("Predict how many months forward:", min_value=1, step=1)



# -- Calculate Button Logic
if st.sidebar.button("Calculate"):
    monthly_rate = apy / 12
    running_balance = balance

    rows = []

    # ----- Month-by-month table -----
    for month in range(1, months + 1):
        start_bal = running_balance
        interest = start_bal * monthly_rate
        running_balance = start_bal + interest + monthly_deposit

        rows.append({
            "Month": month,
            "Starting Balance": round(start_bal, 2),
            "Interest Earned": round(interest, 2),
            "Deposit": monthly_deposit,
            "Ending Balance": round(running_balance, 2)
        })

    df = pd.DataFrame(rows)

    # ----- Yearly Summary -----
    yearly = []
    for year in range((months - 1)//12 + 1):
        yearly_df_temp = df.iloc[year*12:(year+1)*12]
        yearly.append({
            "Year": year + 1,
            "Total Interest": round(yearly_df_temp["Interest Earned"].sum(), 2),
            "Total Deposits": round(yearly_df_temp["Deposit"].sum(), 2),
            "Ending Balance": round(yearly_df_temp["Ending Balance"].iloc[-1], 2)
        })

    yearly_df = pd.DataFrame(yearly)

    # SAVE RESULTS INTO SESSION STATE
    st.session_state.df = df
    st.session_state.yearly_df = yearly_df



# -- Functions
def statsMonthly():
    st.header("📅 Month-by-Month Breakdown")
    st.dataframe(st.session_state.df)

def statsYearly():
    st.header("📘 Yearly Summary")
    st.dataframe(st.session_state.yearly_df)

def viz():
    st.subheader("📈 Balance Over Time")
    st.line_chart(st.session_state.df["Ending Balance"])



# -- Page Routing With Checks
if options == "Data Statistics":
    if st.session_state.df is None:
        st.warning("Please press **Calculate** to continue.")
    else:
        statsMonthly()
        statsYearly()

else:
    if st.session_state.df is None:
        st.warning("Please press **Calculate** to continue.")
    else:
        viz()
