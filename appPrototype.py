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

import random
import time
import difflib

# ---- Load CSV with Q/A ----
@st.cache_data
def load_qa():
    df = pd.read_csv("exampleData.csv")
    return df

qa_df = load_qa()

# ---- Fuzzy match function ----
def get_best_answer(user_input):
    questions = qa_df["question"].tolist()
    
    # find closest match
    match = difflib.get_close_matches(user_input.lower(), [q.lower() for q in questions], n=1, cutoff=0.3)
    
    if match:
        matched_question = match[0]
        answer_row = qa_df[qa_df["question"].str.lower() == matched_question].iloc[0]
        return answer_row["answer"]
    else:
        return random.choice([
            "I'm not sure I can answer that question yet, I'm still learning!",
            "Hmm… I don't think my data covers that one.",
            "Good question! I don't have that answer yet."
        ])

# ---- UI Header ----
st.title("💬 Savings Calculator Chatbot")
st.caption("Disclaimer!: This tiny bot answers questions using a CSV file, therefore it might have some limitations.")

# ---- Initialize chat history ----
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! Ask me anything about savings, APY, or your calculator 👇"}
    ]

# ---- Display history ----
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---- User input ----
if prompt := st.chat_input("Ask me a question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        answer = get_best_answer(prompt)

        # typing effect
        for chunk in answer.split():
            full_response += chunk + " "
            time.sleep(0.03)
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

    # add bot response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

