import streamlit as st
import pandas as pd
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
Invest in high-yield bond + Borrow additional funds → Invest in treasury bond + Reinvest all interest
""")

# Sidebar controls
with st.sidebar:
    st.header("Investment Parameters")
    initial_investment = st.number_input("Initial Investment (₹)", 
                                       min_value=10000, 
                                       value=100000, 
                                       step=10000)
    
    high_yield_rate = st.slider("High-Yield Bond Rate (% p.a.)", 
                              min_value=1.0, 
                              max_value=30.0, 
                              value=14.0, 
                              step=0.1)
    
    treasury_rate = st.slider("Treasury Bond Rate (% p.a.)", 
                            min_value=1.0, 
                            max_value=20.0, 
                            value=12.0, 
                            step=0.1)
    
    borrowing_rate = st.slider("Borrowing Rate (% p.a.)", 
                             min_value=1.0, 
                             max_value=20.0, 
                             value=10.0, 
                             step=0.1)
    
    months = st.slider("Investment Period (Months)", 
                      min_value=1, 
                      max_value=60, 
                      value=12, 
                      step=1)
    
    leverage_ratio = st.slider("Leverage Ratio", 
                             min_value=1.0, 
                             max_value=3.0, 
                             value=1.0, 
                             step=0.1)

# Calculate borrowed amount
borrowed_amount = initial_investment * leverage_ratio

# Monthly rates
monthly_high = high_yield_rate / 12 / 100
monthly_treasury = treasury_rate / 12 / 100
monthly_borrow = borrowing_rate / 12 / 100

# Initialize variables
high_yield_principal = initial_investment
treasury_principal = borrowed_amount
borrowed_balance = borrowed_amount
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
        "High-Yield Interest": high_yield_interest,
        "Treasury Interest": treasury_interest,
        "Total Reinvested": total_reinvestment,
        "Treasury Balance": treasury_principal,
        "Loan Interest Paid": monthly_loan_interest,
        "Cumulative Loan Interest": loan_interest_paid
    })

# Create DataFrame
df = pd.DataFrame(records)

# Final calculations
final_treasury = df.iloc[-1]["Treasury Balance"]
total_loan_cost = borrowed_amount + df.iloc[-1]["Cumulative Loan Interest"]

# Investor's final position
investor_final = high_yield_principal + final_treasury - total_loan_cost
net_profit = investor_final - initial_investment
annualized_return = (net_profit / initial_investment) * (12/months) * 100  # Annualized

# Display summary
st.subheader("📊 Investment Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Your Investment", f"₹{initial_investment:,.0f}")
col2.metric("Borrowed Amount", f"₹{borrowed_amount:,.0f} ({leverage_ratio:,.1f}X)")
col3.metric("Total Invested", f"₹{initial_investment + borrowed_amount:,.0f}")

# Display results
st.subheader("💵 Final Results")
col1, col2, col3 = st.columns(3)
col1.metric("Reinvested Amount Grown To", f"₹{final_treasury:,.0f}")
col2.metric("Total Loan Repayment", f"₹{total_loan_cost:,.0f}")
col3.metric("Your Net Profit", f"₹{net_profit:,.0f}", 
           f"{annualized_return:.1f}% annualized")

# Monthly breakdown
st.subheader("📅 Monthly Breakdown")
st.dataframe(df.style.format({
    "High-Yield Interest": "₹{:,.0f}",
    "Treasury Interest": "₹{:,.0f}",
    "Total Reinvested": "₹{:,.0f}",
    "Treasury Balance": "₹{:,.0f}",
    "Loan Interest Paid": "₹{:,.0f}",
    "Cumulative Loan Interest": "₹{:,.0f}"
}))

# Visualizations
fig, ax = plt.subplots(figsize=(10, 6))

# Plot growth curves
ax.plot(df["Month"], df["Treasury Balance"], 
        label="Reinvested Amount", color='#4f8bf9', linewidth=2)
ax.plot(df["Month"], [borrowed_amount + x for x in df["Cumulative Loan Interest"]], 
        label="Loan Balance", color='#d62728', linestyle='--')
ax.plot(df["Month"], [initial_investment + x for x in df["Treasury Balance"] - df["Cumulative Loan Interest"] - borrowed_amount], 
        label="Your Net Value", color='#2ca02c', linewidth=3)

ax.set_title("Investment Growth Over Time", fontsize=16)
ax.set_xlabel("Months", fontsize=12)
ax.set_ylabel("Amount (₹)", fontsize=12)
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_facecolor('#f5f5f5')

st.pyplot(fig)

# Calculation explanation
with st.expander("🧮 See Detailed Calculations"):
    st.markdown(f"""
    ### Monthly Calculation Process:
    
    1. **High-Yield Bond ({high_yield_rate}% p.a.)**
       - Principal: ₹{initial_investment:,.0f} (remains constant)
       - Monthly interest: ₹{initial_investment:,.0f} × ({high_yield_rate}/12)% = ₹{high_yield_interest:,.0f}
    
    2. **Treasury Bond ({treasury_rate}% p.a.)**
       - Borrowed principal: ₹{borrowed_amount:,.0f}
       - Monthly interest: ₹{borrowed_amount:,.0f} × ({treasury_rate}/12)% = ₹{treasury_interest:,.0f}
    
    3. **Reinvestment**
       - Total monthly reinvestment: ₹{high_yield_interest:,.0f} + ₹{treasury_interest:,.0f} = ₹{total_reinvestment:,.0f}
       - Compounded monthly at {treasury_rate/12:.3f}%
    
    4. **Loan Costs ({borrowing_rate}% p.a.)**
       - Monthly interest: ₹{borrowed_amount:,.0f} × ({borrowing_rate}/12)% = ₹{monthly_loan_interest:,.0f}
    
    ### Final Position After {months} Months:
    - Reinvested amount grows to: ₹{final_treasury:,.0f}
    - Repay loan: ₹{borrowed_amount:,.0f} principal + ₹{loan_interest_paid:,.0f} interest
    - Your original investment: ₹{initial_investment:,.0f}
    - Net profit: ₹{net_profit:,.0f}
    - Annualized return: {annualized_return:.1f}%
    """)

# Risk disclosure
st.error("""
**⚠️ Important Risks to Consider:**
1. The high-yield bond ({high_yield_rate}%) carries higher default risk than treasury bonds
2. Requires the treasury bond return ({treasury_rate}%) to exceed borrowing cost ({borrowing_rate}%)
3. Monthly compounding assumes perfect reinvestment (may not be realistic)
4. Does not account for taxes, platform fees, or early withdrawal penalties
5. Leverage magnifies both gains and losses
""")
