import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(page_title="Leveraged Bond Reinvestment Simulator", layout="wide")

# Custom styling
st.markdown("""
<style>
    .main {background-color: #f5f5f5;}
    .stSlider>div>div>div>div {background: #4f8bf9;}
    .reportview-container .main .block-container {padding-top: 2rem;}
    h1 {color: #2a3f5f;}
    .css-1aumxhk {background-color: #ffffff; border-radius: 10px; padding: 20px;}
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("💰 Leveraged Bond Reinvestment Simulator")
st.markdown("""
**🧠 Scenario:**  
Invest ₹1L in 14% bond + Borrow ₹1L @10% → Invest in 12% bond + Reinvest all interest in 12% bond
""")

# Parameters
initial_investment = 100000  # ₹1,00,000
high_yield_rate = 14.0       # 14% p.a.
treasury_rate = 12.0         # 12% p.a.
borrowing_rate = 10.0        # 10% p.a.
months = 12                  # 1 year

# Monthly rates
monthly_high = high_yield_rate / 12 / 100
monthly_treasury = treasury_rate / 12 / 100
monthly_borrow = borrowing_rate / 12 / 100

# Initialize variables
high_yield_principal = initial_investment
treasury_principal = initial_investment  # Borrowed amount
borrowed_balance = initial_investment
total_reinvested = 0
loan_interest_paid = 0

# Track monthly values
records = []

for month in range(1, months + 1):
    # Calculate interest from bonds
    high_yield_interest = high_yield_principal * monthly_high
    treasury_interest = treasury_principal * monthly_treasury
    
    # Reinvest all interest into treasury bond
    total_reinvestment = high_yield_interest + treasury_interest
    treasury_principal += total_reinvestment
    total_reinvested += total_reinvestment
    
    # Accrue loan interest
    monthly_loan_interest = borrowed_balance * monthly_borrow
    loan_interest_paid += monthly_loan_interest
    
    # Record monthly values
    records.append({
        "Month": month,
        "14% Bond Interest": high_yield_interest,
        "12% Bond Interest": treasury_interest,
        "Total Reinvested": total_reinvestment,
        "Treasury Balance": treasury_principal,
        "Loan Interest Paid": monthly_loan_interest,
        "Cumulative Loan Interest": loan_interest_paid
    })

# Create DataFrame
df = pd.DataFrame(records)

# Final calculations
final_treasury = df.iloc[-1]["Treasury Balance"]
total_loan_cost = initial_investment + df.iloc[-1]["Cumulative Loan Interest"]  # Principal + interest

# Investor's final position
investor_final = high_yield_principal + final_treasury - total_loan_cost
net_profit = investor_final - initial_investment
annual_return = (net_profit / initial_investment) * 100

# Display results
st.subheader("💵 Final Results After 1 Year")
col1, col2, col3 = st.columns(3)
col1.metric("Total Reinvested Interest", f"₹{final_treasury:,.0f}")
col2.metric("Loan Repayment (Principal + Interest)", f"₹{total_loan_cost:,.0f}")
col3.metric("Investor's Net Profit", f"₹{net_profit:,.0f}", f"{annual_return:.2f}% return")

# Monthly breakdown
st.subheader("📅 Monthly Breakdown")
st.dataframe(df.style.format({
    "14% Bond Interest": "₹{:,.0f}",
    "12% Bond Interest": "₹{:,.0f}",
    "Total Reinvested": "₹{:,.0f}",
    "Treasury Balance": "₹{:,.0f}",
    "Loan Interest Paid": "₹{:,.0f}",
    "Cumulative Loan Interest": "₹{:,.0f}"
}))

# Visualization
fig, ax1 = plt.subplots(figsize=(10, 6))

color = 'tab:blue'
ax1.set_xlabel('Month')
ax1.set_ylabel('Amount (₹)', color=color)
ax1.plot(df["Month"], df["Treasury Balance"], label="Reinvested Amount", color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Cumulative Loan Interest (₹)', color=color)
ax2.plot(df["Month"], df["Cumulative Loan Interest"], label="Loan Interest", color=color, linestyle='--')
ax2.tick_params(axis='y', labelcolor=color)

plt.title("Reinvested Growth vs Loan Interest Accrual")
fig.tight_layout()
st.pyplot(fig)

# Calculation explanation
with st.expander("🔍 Detailed Calculation Steps"):
    st.markdown(f"""
    ### Monthly Process:
    1. **14% Bond:**
       - Principal: ₹{initial_investment:,.0f} (stays constant)
       - Monthly interest: ₹{initial_investment:,.0f} × {monthly_high:.3%} = ₹{high_yield_interest:,.0f}
    
    2. **12% Bond (Borrowed Money):**
       - Principal: ₹{initial_investment:,.0f}
       - Monthly interest: ₹{initial_investment:,.0f} × {monthly_treasury:.3%} = ₹{treasury_interest:,.0f}
    
    3. **Reinvestment:**
       - Total monthly: ₹{high_yield_interest:,.0f} + ₹{treasury_interest:,.0f} = ₹{total_reinvestment:,.0f}
       - Compounded monthly at {monthly_treasury:.3%}
    
    4. **Loan Costs:**
       - Monthly interest: ₹{initial_investment:,.0f} × {monthly_borrow:.3%} = ₹{monthly_loan_interest:,.0f}
       - Total interest after 12 months: ₹{loan_interest_paid:,.0f}
    
    ### Final Position:
    - Reinvested amount grows to: ₹{final_treasury:,.0f}
    - Repay loan: ₹{initial_investment:,.0f} principal + ₹{loan_interest_paid:,.0f} interest
    - Net profit: ₹{net_profit:,.0f} ({annual_return:.2f}% return)
    """)

# Risk disclosure
st.warning("""
**⚠️ Important Risks:**
1. The 14% bond likely carries higher default risk
2. Requires consistent monthly interest payments
3. Assumes no early withdrawal of funds
4. Does not account for taxes or platform fees
5. Liquidity risk if bonds can't be sold when needed
""")
