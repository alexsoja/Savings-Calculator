import streamlit as st
import pandas as pd

st.title("💰 Savings Growth Predictor")

balance = st.number_input("Enter Current Balance:", min_value=0.0)
apy = st.number_input("Enter APY (as decimal, e.g. 0.04 for 4%):", min_value=0.0, max_value=1.0,format="%.4f")
monthly_deposit = st.number_input("Enter Monthly Deposit:", min_value=0.0)
months = st.number_input("Predict how many months forward:", min_value=1, step=1)

if st.button("Calculate"):
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
    st.subheader("📅 Month-by-Month Breakdown")
    st.dataframe(df)

    # ----- Yearly Summary -----
    yearly = []
    for year in range((months - 1)//12 + 1):
        yearly_df = df.iloc[year*12:(year+1)*12]
        yearly.append({
            "Year": year + 1,
            "Total Interest": round(yearly_df["Interest Earned"].sum(), 2),
            "Total Deposits": round(yearly_df["Deposit"].sum(), 2),
            "Ending Balance": round(yearly_df["Ending Balance"].iloc[-1], 2)
        })

    yearly_df = pd.DataFrame(yearly)
    st.subheader("📘 Yearly Summary")
    st.dataframe(yearly_df)

    # ----- Chart -----
    st.subheader("📈 Balance Over Time")
    st.line_chart(df["Ending Balance"])
