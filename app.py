import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Set page config
st.set_page_config(page_title="Bond Reinvestment Simulator", layout="wide")

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
st.title("💰 Bond Reinvestment Simulator")
st.markdown("""
This simulator demonstrates how reinvesting monthly interest from a high-yield bond into a treasury bond 
with proper monthly compounding can potentially increase your annual returns.
""")

# Sidebar inputs
with st.sidebar:
    st.header("Investment Parameters")
    initial_investment = st.number_input("Initial Investment (₹)", min_value=1000, value=100000, step=5000)
    high_yield_rate = st.slider("High-Yield Bond Rate (% p.a.)", 1.0, 20.0, 14.0, 0.1)
    treasury_rate = st.slider("Treasury Bond Rate (% p.a.)", 1.0, 10.0, 6.5, 0.1)
    investment_period = st.slider("Investment Period (Years)", 1, 30, 5)
    
    st.markdown("---")
    st.markdown("**How it works:**")
    st.markdown("""
    1. Invest in a high-yield bond (e.g., 14% p.a.)
    2. Receive monthly interest payments
    3. Reinvest those payments in a treasury bond (e.g., 6.5% p.a.)
    4. Both bonds compound monthly
    """)

# Calculate monthly returns with proper compounding
def calculate_returns(initial, high_rate, low_rate, years):
    months = years * 12
    monthly_high_rate = high_rate / 12 / 100  # Monthly rate for high-yield bond
    monthly_low_rate = low_rate / 12 / 100    # Monthly rate for treasury bond
    
    # Initialize data structures
    data = []
    principal = initial
    treasury_principal = 0  # This will hold all reinvested amounts and their growth
    
    for month in range(1, months + 1):
        # Calculate interest from high-yield bond (simple interest paid out monthly)
        interest = principal * monthly_high_rate
        
        # Add this interest to treasury principal (new deposit)
        treasury_principal += interest
        
        # Calculate treasury bond growth (compounding monthly on entire treasury balance)
        treasury_growth = treasury_principal * monthly_low_rate
        treasury_principal += treasury_growth
        
        # Update totals
        total_value = principal + treasury_principal
        
        # Append to data
        data.append({
            "Month": month,
            "Principal": principal,
            "Monthly Interest": interest,
            "Treasury Principal": treasury_principal,
            "Treasury Growth": treasury_growth,
            "Total Value": total_value
        })
    
    return pd.DataFrame(data)

# Run simulation
df = calculate_returns(initial_investment, high_yield_rate, treasury_rate, investment_period)

# Calculate metrics
final_value = df.iloc[-1]["Total Value"]
total_interest = final_value - initial_investment
annualized_return = ((final_value / initial_investment) ** (1/investment_period) - 1) * 100
simple_return = (total_interest / initial_investment) * 100

# Display results
col1, col2, col3 = st.columns(3)
col1.metric("Initial Investment", f"₹{initial_investment:,.0f}")
col2.metric("Final Value", f"₹{final_value:,.0f}", delta=f"₹{total_interest:,.0f}")
col3.metric("Annualized Return", f"{annualized_return:.1f}%", delta=f"{simple_return/investment_period:.1f}% p.a.")

# Plot results
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df["Month"], df["Principal"], label="High-Yield Bond", color='#4f8bf9', linewidth=2)
ax.plot(df["Month"], df["Treasury Principal"], label="Treasury Bond (Reinvested)", color='#2ca02c', linewidth=2)
ax.plot(df["Month"], df["Total Value"], label="Total Portfolio Value", color='#ff7f0e', linewidth=2, linestyle='--')

ax.set_title("Investment Growth with Monthly Compounding", fontsize=16)
ax.set_xlabel("Months", fontsize=12)
ax.set_ylabel("Amount (₹)", fontsize=12)
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_facecolor('#f5f5f5')

st.pyplot(fig)

# Show data table
st.subheader("Monthly Breakdown")
st.dataframe(df.tail(12).style.format({
    "Principal": "{:,.2f}",
    "Monthly Interest": "{:,.2f}",
    "Treasury Principal": "{:,.2f}",
    "Treasury Growth": "{:,.2f}",
    "Total Value": "{:,.2f}"
}), height=400)

# Detailed explanation
with st.expander("Detailed Calculation Explanation"):
    st.markdown(f"""
    ### Monthly Calculation Breakdown (First 3 Months Example)
    
    **Initial Investment:** ₹{initial_investment:,.2f} at {high_yield_rate}% p.a. (High-Yield Bond)
    **Reinvestment Rate:** {treasury_rate}% p.a. (Treasury Bond)
    
    **Month 1:**
    - High-Yield Interest = ₹{initial_investment:,.2f} × ({high_yield_rate}/12)% = ₹{initial_investment * high_yield_rate/12/100:,.2f}
    - Treasury Balance = ₹{initial_investment * high_yield_rate/12/100:,.2f} (initial deposit)
    - Treasury Growth = ₹{initial_investment * high_yield_rate/12/100:,.2f} × ({treasury_rate}/12)% = ₹{initial_investment * high_yield_rate/12/100 * treasury_rate/12/100:,.2f}
    - Total Treasury = ₹{initial_investment * high_yield_rate/12/100 * (1 + treasury_rate/12/100):,.2f}
    
    **Month 2:**
    - High-Yield Interest = Same as Month 1 (principal unchanged)
    - Treasury Balance grows with new deposit + previous balance compounding
    - This pattern continues each month with compounding on the treasury balance
    
    **After {investment_period} years ({investment_period*12} months):**
    - Final Portfolio Value = ₹{final_value:,.2f}
    - Annualized Return = {annualized_return:.2f}%
    """)

# Add a disclaimer
st.warning("""
**Disclaimer**: This is a mathematical simulation assuming perfect conditions. Actual investment returns may vary 
due to market conditions, bond defaults, taxes, fees, and other factors. The high yield bond's 14% return carries 
higher risk than treasury bonds. Past performance is not indicative of future results. 
Always consult with a financial advisor before making investment decisions.
""")
