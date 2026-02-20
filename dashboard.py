import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime , date
import os
import json

st.set_page_config(page_title="My Finance Tracker", layout="wide")

st.title ("Personal Finance Tracker")
DATA_FILE ="transactions.csv"
BUDGETS_FILE ="budgets.json"

def load_budgets():
    if os.path.exists(BUDGETS_FILE):
        with open(BUDGETS_FILE, "r") as f:
            return json.load(f)
    return {
        "Food": 25000,
        "Transport": 15000,
        "Rent": 60000,
        "Utilities": 10000,
        "Entertainment": 8000,
        "School/Tuition": 20000,
        "Other": 10000,
    }
def save_budgets (budgets_dict):
     with open(BUDGETS_FILE, "w") as f:
               json.dump(budgets_dict, f, indent=2)

if 'budgets' not in st.session_state:
     st.session_state.budgets = load_budgets()
                    

tab1, tab2, tab3, tab4 = st.tabs(["Add Transaction", "Dashboard", "Raw Data", "Budgets & Goals"])

with tab1:
    with st.form("new_transaction", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            t_date = st.date_input("Date", value=date.today())
        with col2:
            t_type = st.radio("Type", ["Income", "Expense"], horizontal=True)

        col3, col4 = st.columns(2)
        with col3:
            t_category = st.selectbox("Category", list(st.session_state.budgets.keys()) + ["Salary", "Freelance", "Other"])
        with col4:
            t_amount = st.number_input("Amount (LKR)", min_value=0.0, step=100.0, format="%.0f")

        t_desc = st.text_input("Description / Notes")

        submitted = st.form_submit_button("Add Transaction", use_container_width=True)

        if submitted and t_amount > 0:
            amount_signed = t_amount if t_type == "Income" else -t_amount
            new_row = pd.DataFrame({
                "Date": [t_date],
                "Type": [t_type],
                "Category": [t_category],
                "Amount": [amount_signed],
                "Description": [t_desc]
            })

            if os.path.exists(DATA_FILE):
                new_row.to_csv(DATA_FILE, mode="a", header=False, index=False)
            else:
                new_row.to_csv(DATA_FILE, index=False)

            st.success(f"Added: {t_type} {t_amount:,.0f} LKR – {t_category}")
            st.balloons()  


with tab2:
    if not os.path.exists(DATA_FILE):
        st.info("No transactions yet. Add some in the first tab! 🚀")
    else:
        df = pd.read_csv(DATA_FILE)
        df["Date"] = pd.to_datetime(df["Date"])

        
        st.subheader("View Period")
        period_option = st.selectbox(
            "Select view",
            ["Current Month", "Last Month", "This Year", "Custom Range"],
            index=0
        )

        today = datetime.now().date()
        if period_option == "Current Month":
            start_d = date(today.year, today.month, 1)
            end_d = today
        elif period_option == "Last Month":
            first_this_month = date(today.year, today.month, 1)
            start_d = (first_this_month - pd.Timedelta(days=1)).replace(day=1)
            end_d = first_this_month - pd.Timedelta(days=1)
        elif period_option == "This Year":
            start_d = date(today.year, 1, 1)
            end_d = today
        else:  
            col1, col2 = st.columns(2)
            start_d = col1.date_input("From", value=date(today.year, today.month-1, 1))
            end_d = col2.date_input("To", value=today)

        
        mask = (df["Date"].dt.date >= start_d) & (df["Date"].dt.date <= end_d)
        filtered_df = df[mask]

        if filtered_df.empty:
            st.warning("No transactions in selected period.")
        else:
            income = filtered_df[filtered_df["Amount"] > 0]["Amount"].sum()
            expense = filtered_df[filtered_df["Amount"] < 0]["Amount"].abs().sum()
            net = income - expense

            colA, colB, colC = st.columns(3)
            colA.metric("Income", f"{income:,.0f} LKR")
            colB.metric("Expenses", f"{expense:,.0f} LKR", delta_color="inverse")
            colC.metric("Net", f"{net:,.0f} LKR", delta=f"{net:+,.0f}")

            
            fig_pie = px.pie(
                filtered_df[filtered_df["Amount"] < 0],
                values="Amount", names="Category",
                title=f"Expenses by Category ({period_option})",
                hole=0.4
            )
            st.plotly_chart(fig_pie, width='stretch')

            
            daily = filtered_df.groupby(filtered_df["Date"].dt.date)["Amount"].sum().reset_index()
            fig_line = px.line(daily, x="Date", y="Amount", title="Daily Net Flow")
            st.plotly_chart(fig_line, width='stretch')




with tab3:
    if os.path.exists(DATA_FILE):
        st.dataframe(pd.read_csv(DATA_FILE).sort_values("Date", ascending=False))
    else:
        st.info("No data yet.")




with tab4:
    st.subheader("Monthly Budgets (LKR)")

    
    updated_budgets = {}
    for cat, val in st.session_state.budgets.items():
        new_val = st.number_input(f"{cat}", value=val, step=500, key=f"budget_{cat}")
        updated_budgets[cat] = new_val

    if st.button("Save Budget Changes"):
        st.session_state.budgets = updated_budgets
        save_budgets(updated_budgets)
        st.success("Budgets saved!")

   
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df["Date"] = pd.to_datetime(df["Date"])

       
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_exp = df[(df["Date"] >= month_start) & (df["Amount"] < 0)].copy()
        current_exp["Amount"] = current_exp["Amount"].abs()

        exp_by_cat = current_exp.groupby("Category")["Amount"].sum().to_dict()

        st.subheader("Current Month Budget Progress")
        for cat, budget in st.session_state.budgets.items():
            spent = exp_by_cat.get(cat, 0)
            percent = (spent / budget * 100) if budget > 0 else 0
            remaining = budget - spent

            cols = st.columns([4, 2, 2])
            with cols[0]:
                st.write(f"**{cat}**")
            with cols[1]:
                st.write(f"{spent:,.0f} / {budget:,.0f}")
            with cols[2]:
                color = "red" if percent > 100 else "orange" if percent > 80 else "green"
                st.progress(min(percent / 100, 1.0))
                st.caption(f"{percent:.0f}% – {'Over!' if percent > 100 else f'{remaining:,.0f} left'}")

        st.caption("Note: Budget progress shows current calendar month only.")

  
    st.divider()
    st.subheader("Savings Goal Example")
    goal_amount = st.number_input("Target amount (LKR)", value=300000, step=10000)
    current_savings = st.session_state.get("savings", 0)  
    st.progress(current_savings / goal_amount if goal_amount > 0 else 0)
    st.write(f"Progress: {current_savings:,.0f} / {goal_amount:,.0f} LKR")