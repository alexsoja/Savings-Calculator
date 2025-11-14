import streamlit as st
import pandas as pd

if st.button("🔄 Reload Page"):
    st.session_state.clear()
    st.rerun()
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

# ------------------------------- #
# ------- ANSWER DETECTOR ------- #
# ------------------------------- #

# Helper Function
def best_match_from(df_subset, user_lower):
    if df_subset.empty:
        return "I'm not sure about that one yet!", None

    questions = df_subset["question"].tolist()
    scores = [
        difflib.SequenceMatcher(None, user_lower, q.lower()).ratio()
        for q in questions
    ]

    best_idx = scores.index(max(scores))
    best_question = df_subset.iloc[best_idx]["question"] # Returns the best question detected (useful for debugging and undestanding)
    best_answer = df_subset.iloc[best_idx]["answer"]

    return best_answer, best_question


import re

def get_best_answer(user_input):
    user_lower = user_input.lower()

    # --- 1. CDs ---
    if re.search(r"\b(cd|certificate of deposit)\b", user_lower):
        subset = qa_df[qa_df["question"].str.contains(r"\b(cd|certificate of deposit)\b", case=False, regex=True)]
        return best_match_from(subset, user_lower)

    # --- 2. Credit Cards ---
    if "credit card" in user_lower:
        subset = qa_df[qa_df["question"].str.contains("credit card", case=False)]
        return best_match_from(subset, user_lower)

    # --- 3. Debit Cards ---
    if "debit" in user_lower:
        subset = qa_df[qa_df["question"].str.contains("debit", case=False)]
        return best_match_from(subset, user_lower)

    # --- 4. Savings Accounts ---
    if any(word in user_lower for word in ["savings", "hysa", "bank account"]):
        subset = qa_df[qa_df["question"].str.contains("savings|hysa|bank account", case=False, regex=True)]
        return best_match_from(subset, user_lower)

    # --- 5. APY ---
    if "apy" in user_lower:
        subset = qa_df[qa_df["question"].str.contains("apy", case=False)]
        return best_match_from(subset, user_lower)

    # --- 6. ETFs / Investing ---
    if any(word in user_lower for word in ["etf", "stock", "bond", "invest"]):
        subset = qa_df[qa_df["question"].str.contains("etf|stock|bond|invest", case=False, regex=True)]
        return best_match_from(subset, user_lower)

    # --- DEFAULT: All questions ---
    return best_match_from(qa_df, user_lower)


# ------------------------------- #
# ---------- CHAT BOT ----------- #
# ------------------------------- #


# ---- UI Header ----
st.title("💬 Savings Calculator Chatbot")
st.caption("Disclaimer: This bot answers questions using a CSV file. Accuracy depends on the questions inside your dataset.")

# ---- Initialize chat history ----
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! Ask me anything about savings, APY, or your calculator 👇"},
        {"role": "meta", "matched_q": None}  # placeholder for matched questions
    ]

# ---- Display Chat History ----
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(message["content"])
            # If matched question metadata exists, show it
            if "matched_q" in message and message["matched_q"]:
                st.caption(f"Matched question: **{message['matched_q']}**")
    elif message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])

# ---- User input ----
if prompt := st.chat_input("Ask me a question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    answer, matched_question = get_best_answer(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        # typing effect
        for chunk in answer.split():
            full_response += chunk + " "
            time.sleep(0.03)
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

        # Show matched question
        if matched_question:
            st.caption(f"Matched question: **{matched_question}**")

    # Save bot response to history (including matched question for future display)
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "matched_q": matched_question
    })


