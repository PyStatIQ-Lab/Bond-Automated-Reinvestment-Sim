import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(page_title="Dual Bond Reinvestment Simulator", layout="wide")

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
st.title("💰 Dual Bond Reinvestment Simulator")
st.markdown("""
This simulator models:
1. ₹1 lakh invested in 14% monthly bond
2. Platform lends additional ₹1 lakh at 10%
3. Lent amount invested in 12% monthly bond
4. All 14% bond interest reinvested in 12% bond
""")

# Input parameters
investor_capital = 100000  # ₹1 lakh
high_yield_rate = 14.0     # 14% p.a.
treasury_rate = 12.0       # 12% p.a.
borrowing_rate = 10.0      # 10% p.a.
investment_period = 5      # 5 years

# Calculate monthly returns
def calculate_returns(investor_cap, high_rate, treasury_rate, borrow_rate, years):
    months = years * 12
    monthly_high_rate = high_rate / 12 / 100
    monthly_treasury_rate = treasury_rate / 12 / 100
    monthly_borrow_rate = borrow_rate / 12 / 100
    
    # Initialize balances
    high_yield_principal = investor_cap  # ₹1 lakh at 14%
    treasury_principal = investor_cap    # Additional ₹1 lakh at 12%
    borrowed_balance = investor_cap      # ₹1 lakh loan at 10%
    
    data = []
    
    for month in range(1, months + 1):
        # Calculate interest from 14% bond
        high_yield_interest = high_yield_principal * monthly_high_rate
        
        # Calculate interest from 12% bond (on both principal and reinvestments)
        treasury_interest = treasury_principal * monthly_treasury_rate
        
        # Reinvest the 14% bond interest into 12% bond
        treasury_principal += high_yield_interest
        
        # Add treasury interest to treasury principal (compounding)
        treasury_principal += treasury_interest
        
        # Accrue interest on borrowed amount
        borrowing_cost = borrowed_balance * monthly_borrow_rate
        borrowed_balance += borrowing_cost
        
        # Total assets and net value
        total_assets = high_yield_principal + treasury_principal
        net_value = total_assets - borrowed_balance
        
        data.append({
            "Month": month,
            "14% Bond Principal": high_yield_principal,
            "14% Bond Interest": high_yield_interest,
            "12% Bond Principal": treasury_principal,
            "12% Bond Interest": treasury_interest,
            "Borrowed Balance": borrowed_balance,
            "Borrowing Cost": borrowing_cost,
            "Total Assets": total_assets,
            "Net Value": net_value
        })
    
    return pd.DataFrame(data)

# Run simulation
df = calculate_returns(
    investor_capital,
    high_yield_rate,
    treasury_rate,
    borrowing_rate,
    investment_period
)

# Calculate final metrics
final_assets = df.iloc[-1]["Total Assets"]
final_borrowed = df.iloc[-1]["Borrowed Balance"]
investor_final = df.iloc[-1]["Net Value"]

total_return = investor_final - investor_capital
annualized_return = ((investor_final / investor_capital) ** (1/investment_period) - 1) * 100

# Display results
st.subheader("Investment Structure")
col1, col2, col3 = st.columns(3)
col1.metric("Investor's Capital", "₹1,00,000", "14% bond")
col2.metric("Platform Loan", "₹1,00,000", "10% interest")
col3.metric("Total Bond Investment", "₹2,00,000", "₹1L @14% + ₹1L @12%")

st.subheader("Final Results After " + str(investment_period) + " Years")
col1, col2, col3 = st.columns(3)
col1.metric("Total Assets Grown", f"₹{final_assets:,.0f}")
col2.metric("Loan + Interest Owed", f"₹{final_borrowed:,.0f}")
col3.metric("Investor's Net Value", f"₹{investor_final:,.0f}", 
           f"{annualized_return:.1f}% p.a.")

# Plot results
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df["Month"], df["14% Bond Principal"], label="14% Bond", color='#4f8bf9', linestyle='--')
ax.plot(df["Month"], df["12% Bond Principal"], label="12% Bond (with Reinvestment)", color='#2ca02c')
ax.plot(df["Month"], df["Borrowed Balance"], label="Loan Balance", color='#d62728')
ax.plot(df["Month"], df["Net Value"], label="Investor's Net Worth", color='#ff7f0e', linewidth=3)

ax.set_title("Investment Growth with Dual Bonds and Leverage", fontsize=16)
ax.set_xlabel("Months", fontsize=12)
ax.set_ylabel("Amount (₹)", fontsize=12)
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_facecolor('#f5f5f5')

st.pyplot(fig)

# Show detailed table
st.subheader("Monthly Breakdown (Last 12 Months)")
st.dataframe(df.tail(12).style.format({
    "14% Bond Principal": "{:,.0f}",
    "14% Bond Interest": "{:,.0f}",
    "12% Bond Principal": "{:,.0f}",
    "12% Bond Interest": "{:,.0f}",
    "Borrowed Balance": "{:,.0f}",
    "Borrowing Cost": "{:,.0f}",
    "Total Assets": "{:,.0f}",
    "Net Value": "{:,.0f}"
}))

# Calculation explanation
with st.expander("How the Calculation Works"):
    st.markdown("""
    **Monthly Process:**
    1. ₹1 lakh in 14% bond earns monthly interest (14%/12 = 1.1667%)
    2. ₹1 lakh loan is invested in 12% bond (earning 1% monthly)
    3. The 14% bond's interest is reinvested into the 12% bond
    4. The 12% bond compounds monthly on:
       - Original ₹1 lakh principal
       - All reinvested 14% bond interest
       - Its own accumulated interest
    5. The ₹1 lakh loan accrues interest at 10% (0.833% monthly)
    
    **Key Points:**
    - The 14% bond principal remains constant (only interest is withdrawn)
    - The 12% bond grows through both reinvestment and compounding
    - The loan balance grows at 10% until repayment
    - Net value = (14% bond + 12% bond) - loan balance
    """)

# Risk disclosure
st.error("""
**Important Risks:**
- The 14% bond likely carries higher default risk
- Requires the 12% bond to outperform the 10% borrowing cost
- Taxes and fees would reduce actual returns
- Early withdrawal penalties could affect results
- Liquidity risk if bonds can't be sold when needed
""")
