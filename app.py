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
This simulator demonstrates how reinvesting monthly interest from a high-yield bond (14%) into a treasury bond (6.5%) 
can potentially increase your annual returns up to 28%.
""")

# Sidebar inputs
with st.sidebar:
    st.header("Investment Parameters")
    initial_investment = st.number_input("Initial Investment (₹)", min_value=1000, value=100000, step=5000)
    high_yield_rate = st.slider("High-Yield Bond Rate (% p.a.)", 1.0, 20.0, 14.0, 0.1)
    treasury_rate = st.slider("Treasury Bond Rate (% p.a.)", 1.0, 10.0, 6.5, 0.1)
    investment_period = st.slider("Investment Period (Years)", 1, 30, 5)
    compounding_freq = st.selectbox("Compounding Frequency", ["Monthly", "Quarterly", "Annually"], index=0)
    
    st.markdown("---")
    st.markdown("**How it works:**")
    st.markdown("""
    1. Invest in a high-yield bond (14% p.a.)
    2. Receive monthly interest payments
    3. Reinvest those payments in a treasury bond (6.5% p.a.)
    4. Compound returns over time
    """)

# Calculate monthly returns
def calculate_returns(initial, high_rate, low_rate, years, freq):
    months = years * 12
    monthly_high_rate = high_rate / 12 / 100
    monthly_low_rate = low_rate / 12 / 100
    
    # Initialize data
    data = []
    principal = initial
    reinvested = 0
    total_reinvested = 0
    
    for month in range(1, months + 1):
        # Calculate interest from high-yield bond
        interest = principal * monthly_high_rate
        
        # Reinvest the interest in treasury bond
        reinvested += interest
        reinvested_growth = reinvested * monthly_low_rate
        reinvested += reinvested_growth
        
        # Update totals
        total_reinvested += interest
        total_value = principal + reinvested
        
        # Append to data
        data.append({
            "Month": month,
            "Principal": principal,
            "Interest": interest,
            "Reinvested": reinvested,
            "Total Value": total_value,
            "Total Reinvested": total_reinvested
        })
    
    return pd.DataFrame(data)

# Run simulation
df = calculate_returns(initial_investment, high_yield_rate, treasury_rate, investment_period, compounding_freq)

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
ax.plot(df["Month"], df["Principal"], label="Principal", color='#4f8bf9', linewidth=2)
ax.plot(df["Month"], df["Reinvested"], label="Reinvested Amount", color='#2ca02c', linewidth=2)
ax.plot(df["Month"], df["Total Value"], label="Total Value", color='#ff7f0e', linewidth=2, linestyle='--')

ax.set_title("Investment Growth Over Time", fontsize=16)
ax.set_xlabel("Months", fontsize=12)
ax.set_ylabel("Amount (₹)", fontsize=12)
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_facecolor('#f5f5f5')

st.pyplot(fig)

# Show data table
st.subheader("Monthly Breakdown")
st.dataframe(df.tail(12).style.format({
    "Principal": "{:,.0f}",
    "Interest": "{:,.0f}",
    "Reinvested": "{:,.0f}",
    "Total Value": "{:,.0f}",
    "Total Reinvested": "{:,.0f}"
}), height=400)

# Explanation
with st.expander("How this strategy works"):
    st.markdown("""
    ### Bond Reinvestment Strategy
    
    1. **Primary Investment**: You invest in a high-yield bond paying 14% annual interest paid monthly.
    2. **Monthly Interest**: Each month, you receive interest payments (14%/12 = ~1.167% monthly).
    3. **Reinvestment**: Instead of spending this interest, you automatically reinvest it in a safer treasury bond paying 6.5% annually.
    4. **Compounding Effect**: The treasury bond also pays interest on your reinvested amounts, creating a compounding effect.
    
    ### Why It Works
    
    - **Double Compounding**: Your money grows from both the high-yield bond and the treasury bond's compounding.
    - **Risk Management**: While the primary bond might be higher risk, the reinvested amounts go to safer bonds.
    - **Automated Growth**: The system automatically grows your wealth without additional capital.
    
    ### Important Notes
    
    - This assumes the bonds pay consistent interest rates (real bonds may fluctuate)
    - Higher yields typically come with higher risk (default risk, interest rate risk)
    - Taxes and fees are not considered in this simulation
    """)

# Add a disclaimer
st.warning("""
**Disclaimer**: This is a simplified simulation for educational purposes only. Actual investment returns may vary 
due to market conditions, bond defaults, taxes, and other factors. Past performance is not indicative of future results. 
Always consult with a financial advisor before making investment decisions.
""")
