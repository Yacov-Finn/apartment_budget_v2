# app.py
import streamlit as st
from utils.calculate_max_mortgage_and_stamp_duty import calculate_mort_and_tax
import pandas as pd
from io import BytesIO
st.set_page_config(page_title="Apartment Journey", page_icon="🏠")

# === Oleh Hadash purchase tax helper ===
def calc_purchase_tax_oleh(price: float) -> float:
    """
    Purchase tax for Oleh Hadash (single residential home).
    Brackets (approx., as commonly referenced):
      0      – 1,978,745   : 0%
      1,978,745 – 6,055,070: 0.5%
      6,055,070 – 20,183,565: 8%
      20,183,565+          : 10%
    """
    brackets = [
        (0, 1_978_745, 0.00),
        (1_978_745, 6_055_070, 0.005),
        (6_055_070, 20_183_565, 0.08),
        (20_183_565, float("inf"), 0.10),
    ]
    tax = 0.0
    for lower, upper, rate in brackets:
        if price <= lower:
            break
        taxable = min(price, upper) - lower
        if taxable > 0:
            tax += taxable * rate
    return tax
# === End of Oleh Hadash helper ===

# --- simple router (one file) ---
if "page" not in st.session_state:
    st.session_state.page = "home"

def go(page_name: str):
    st.session_state.page = page_name
    st.rerun()

# --- HOME ---
if st.session_state.page == "home":
    st.markdown(
        """
        <h1 style="text-align:center; margin-top:0;">
          Let's start our journey towards an apartment in Israel!
        </h1>
        """,
        unsafe_allow_html=True,
    )
    st.image("Jerusalem1.jpg", caption="Jerusalem • Old & Modern", width="stretch")
    # Display text explaining about the app and what it provides
    st.write(
        """
        Welcome to the Apartment Journey app! This comprehensive tool is designed to guide you through the complex process of purchasing an apartment in Israel.
        
        Based on our extensive experience, we've found that many English-speaking investors and home buyers don't receive complete information about all the costs associated with property purchases in Israel. Our platform provides transparent calculations and detailed explanations of every expense involved in the apartment buying process.
        
        Whether you're a first-time buyer, seasoned investor, or relocating to Israel, this tool will help you make informed financial decisions by providing accurate cost estimates and budget planning assistance.
        """)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ I know the deal I'm interested in", use_container_width=True):
            go("known_basics")
    with col2:
        if st.button("🤔 Help me build a budget", use_container_width=True):
            go("unknown_basics")

# --- KNOWN DEAL BASICS PAGE ---
elif st.session_state.page == "known_basics":
    st.title("✅ I already know the deal - Deal Basics")
    st.write("Great! Let's collect the basic details of your chosen apartment deal.")
    
    # The user will enter the price of the deal he was offered in NIS
    price = st.number_input("Enter the price of the deal (NIS)", min_value=0)
    # The user will enter wether he is an Israeli citizen or not
    is_israeli = st.checkbox("I am an Israeli citizen")
    # The user will enter wether this is his first apartment or not
    is_first_apartment = st.checkbox("This is my first apartment")
    # The user will enter wether he is an Oleh Hadash or not
    is_oleh = st.checkbox("I am an Oleh Hadash (new immigrant)")

    # The user will enter the amount IN nis he wants to take as a mortgage
    mortgage_amount = st.number_input("Enter the amount you want to take as a mortgage (NIS)", min_value=0)
    
    if price > 0:
        mortgage, stamp_duty = calculate_mort_and_tax(price, is_israeli, is_first_apartment, mortgage_amount)

        # Override with Oleh brackets if applicable
        if is_oleh and is_first_apartment:
            stamp_duty = calc_purchase_tax_oleh(price)

        if mortgage_amount > mortgage:
            st.error(f"The maximum mortgage you can take is {mortgage:,.0f} NIS. Please adjust your desired mortgage amount.")
        else:
            st.success(f"The maximum mortgage you can take is {mortgage:,.0f} NIS.")
            st.info(f"The purchase tax for this deal is {stamp_duty:,.0f} NIS.")

        # Store data in session state
        st.session_state.known_data = {
            'price': price,
            'is_israeli': is_israeli,
            'is_first_apartment': is_first_apartment,
            'is_oleh': is_oleh,                 # <— add this
            'mortgage_amount': mortgage_amount,
            'mortgage': mortgage,
            'stamp_duty': stamp_duty
        }

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Home", use_container_width=True):
            go("home")
    with col2:
        if st.button("Continue: Additional Expenses ➡️", use_container_width=True):
            go("known_expenses")

# --- KNOWN EXPENSES PAGE ---
elif st.session_state.page == "known_expenses":
    st.title("✅ Additional Expenses")
    
    # Check if we have the basic data
    if 'known_data' not in st.session_state:
        st.error("Please complete the deal basics first.")
        if st.button("⬅️ Go to Deal Basics", use_container_width=True):
            go("known_basics")
    else:
        data = st.session_state.known_data
        price = data['price']
        mortgage_amount = data['mortgage_amount']
        
        st.write("Now, let's gather information about any additional expenses related to your apartment deal.")
        
        # Agent fee section
        st.subheader("Agent Fee")
        knows_agent_fee = st.checkbox("I know the agent fee")
        
        if knows_agent_fee:
            agent_fee_pct = st.number_input("Enter the agent fee percentage (%)", min_value=0.0, max_value=100.0, step=0.1)
            agent_fee_nis = st.number_input("Or enter the agent fee amount (NIS)", min_value=0)
            if agent_fee_pct > 0:
                agent_fee = price * (agent_fee_pct / 100) * 1.18
                st.info(f"The agent fee based on the percentage is {agent_fee:,.0f} NIS. (Including 18% VAT)")
            elif agent_fee_nis > 0:
                agent_fee = agent_fee_nis * 1.18
                st.info(f"Agent fee: {agent_fee:,.0f} NIS. (Including 18% VAT)")
            else:
                st.warning("Please enter either a percentage or amount for the agent fee.")
                agent_fee = 0
        else:
            agent_fee = price * 0.015 * 1.18
            st.info(f"Using default agent fee: {agent_fee:,.0f} NIS (1.5% + 18% VAT)")
        
        # Lawyer fee section
        st.subheader("Lawyer Fee")
        knows_lawyer_fee = st.checkbox("I know the lawyer fee")
        
        if knows_lawyer_fee:
            lawyer_fee_pct = st.number_input("Enter the lawyer fee percentage (%)", min_value=0.0, max_value=100.0, step=0.1)
            lawyer_fee_nis = st.number_input("Or enter the lawyer fee amount (NIS)", min_value=0)
            if lawyer_fee_pct > 0:
                lawyer_fee = price * (lawyer_fee_pct / 100) * 1.18
                st.info(f"The lawyer fee based on the percentage is {lawyer_fee:,.0f} NIS. (Including 18% VAT)")
            elif lawyer_fee_nis > 0:
                lawyer_fee = lawyer_fee_nis * 1.18
                st.info(f"Lawyer fee: {lawyer_fee:,.0f} NIS. (Including 18% VAT)")
            else:
                st.warning("Please enter either a percentage or amount for the lawyer fee.")
                lawyer_fee = 0
        else:
            lawyer_fee = price * 0.01 * 1.18
            st.info(f"Using default lawyer fee: {lawyer_fee:,.0f} NIS (1% + 18% VAT)")

        # Mortgage advisor fee section
        st.subheader("Mortgage Advisor Fee")
        knows_mortgage_advisor_fee = st.checkbox("I know the mortgage advisor fee")
        
        if knows_mortgage_advisor_fee:
            mortgage_advisor_fee_pct = st.number_input("Enter the mortgage advisor fee percentage (%)", min_value=0.0, max_value=100.0, step=0.1)
            mortgage_advisor_fee_nis = st.number_input("Or enter the mortgage advisor fee amount (NIS)", min_value=0)
            if mortgage_advisor_fee_pct > 0:
                mortgage_advisor_fee = mortgage_amount * (mortgage_advisor_fee_pct / 100) * 1.18
                st.info(f"The mortgage advisor fee based on the percentage is {mortgage_advisor_fee:,.0f} NIS. (Including 18% VAT)")
            elif mortgage_advisor_fee_nis > 0:
                mortgage_advisor_fee = mortgage_advisor_fee_nis * 1.18
                st.info(f"Mortgage advisor fee: {mortgage_advisor_fee:,.0f} NIS. (Including 18% VAT)")
            else:
                st.warning("Please enter either a percentage or amount for the mortgage advisor fee.")
                mortgage_advisor_fee = 0
        else:
            # If the mortgage amount is zero, set advisor fee to zero
            if mortgage_amount == 0:
                mortgage_advisor_fee = 0
                st.info("No mortgage taken, so no mortgage advisor fee.")
            else:
                mortgage_advisor_fee = max(7500, mortgage_amount * 0.01) * 1.18
                st.info(f"Using default mortgage advisor fee: {mortgage_advisor_fee:,.0f} NIS (min. 7500 NIS or 1% + 18% VAT)")
        
        # Update session state with expenses
        st.session_state.known_data.update({
            'agent_fee': agent_fee,
            'lawyer_fee': lawyer_fee,
            'mortgage_advisor_fee': mortgage_advisor_fee
        })
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Deal Basics", use_container_width=True):
                go("known_basics")
        with col2:
            if st.button("Continue: Mortgage Details ➡️", use_container_width=True):
                go("known_mortgage")

# --- KNOWN MORTGAGE PAGE ---
elif st.session_state.page == "known_mortgage":
    st.title("✅ Mortgage Details")
    
    if 'known_data' not in st.session_state:
        st.error("Please complete the previous steps first.")
        if st.button("⬅️ Go to Deal Basics", use_container_width=True):
            go("known_basics")
    else:
        data = st.session_state.known_data
        mortgage_amount = data['mortgage_amount']
        
        st.write("Finally, let's review the details of your mortgage.")
        st.write(f"You have chosen to take a mortgage of {mortgage_amount:,.0f} NIS.")
        
        mortgage_years = st.selectbox("Select the mortgage term (years)", options=[20, 30], index=0)
        if mortgage_years == 30:
            monthly_payment = (mortgage_amount / 1000000) * 5550
        else:
            monthly_payment = (mortgage_amount / 1000000) * 6700
        st.write(f"Your estimated monthly mortgage payment is {monthly_payment:,.0f} NIS.")
        
        # Update session state
        st.session_state.known_data.update({
            'mortgage_years': mortgage_years,
            'monthly_payment': monthly_payment
        })
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Expenses", use_container_width=True):
                go("known_expenses")
        with col2:
            if st.button("Continue: Summary ➡️", use_container_width=True):
                go("known_summary")

# --- KNOWN SUMMARY PAGE ---
elif st.session_state.page == "known_summary":
    st.title("✅ Deal Summary")
    
    if 'known_data' not in st.session_state:
        st.error("Please complete the previous steps first.")
        if st.button("⬅️ Go to Deal Basics", use_container_width=True):
            go("known_basics")
    else:
        data = st.session_state.known_data
        
        st.write("Here's a summary of your apartment deal and associated costs:")
        st.write(f"• Apartment Price: {data['price']:,.0f} NIS")
        st.write(f"• Mortgage Amount: {data['mortgage_amount']:,.0f} NIS")
        st.write(f"• Purchase Tax: {data['stamp_duty']:,.0f} NIS")
        st.write(f"• Agent Fee: {data['agent_fee']:,.0f} NIS")
        st.write(f"• Lawyer Fee: {data['lawyer_fee']:,.0f} NIS")
        st.write(f"• Mortgage Advisor Fee: {data['mortgage_advisor_fee']:,.0f} NIS")
        
        total_costs = data['stamp_duty'] + data['agent_fee'] + data['lawyer_fee'] + data['mortgage_advisor_fee']
        total_investment = data['price'] - data['mortgage_amount'] + total_costs
        
        st.write(f"• Total Additional Costs: {total_costs:,.0f} NIS")
        st.write(f"• Total Cash Investment (Price - Mortgage + Additional Costs): {total_investment:,.0f} NIS")
        st.write(f"• Estimated Monthly Mortgage Payment ({data['mortgage_years']} years): {data['monthly_payment']:,.0f} NIS")
        
        download_summary = st.button("Download Summary as Excel")
        if download_summary:
            summary_data = {
                "Item": ["Apartment Price", "Mortgage Amount", "Purchase Tax", "Agent Fee", "Lawyer Fee", "Mortgage Advisor Fee", "Total Additional Costs", "Total Cash Investment", f"Estimated Monthly Mortgage Payment ({data['mortgage_years']} years)"],
                "Amount (NIS)": [data['price'], data['mortgage_amount'], data['stamp_duty'], data['agent_fee'], data['lawyer_fee'], data['mortgage_advisor_fee'], total_costs, total_investment, data['monthly_payment']]
            }
            df_summary = pd.DataFrame(summary_data)
            towrite = BytesIO()
            df_summary.to_excel(towrite, index=False, sheet_name="Apartment Deal Summary")
            towrite.seek(0)
            st.download_button(label="Click to Download", data=towrite, file_name="apartment_deal_summary.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Mortgage Details", use_container_width=True):
                go("known_mortgage")
        with col2:
            if st.button("🏠 Start New Calculation", use_container_width=True):
                # Clear session state and go home
                if 'known_data' in st.session_state:
                    del st.session_state.known_data
                go("home")

# --- UNKNOWN BASICS PAGE ---
elif st.session_state.page == "unknown_basics":
    st.title("🤔 Help me decide - Budget Basics")
    st.write("Let's start with some basic information to help you find the right apartment deal.")
    
    # The user will enter his down payment in NIS
    budget = st.number_input("Enter your down payment (NIS)", min_value=0, help="This is the cash you have available for the apartment purchase")
    
    # The user will enter whether he is an Israeli citizen or not
    is_israeli = st.checkbox("I am an Israeli citizen")
    
    # The user will enter whether this is his first apartment or not
    is_first_apartment = st.checkbox("This is my first apartment")
    # The user will enter whether he is an Oleh Hadash or not
    is_oleh = st.checkbox("I am an Oleh Hadash (new immigrant)")

    # We will calculate the maximum mortgage he can take based on the max monthly payment and the years
    mortgage_years = st.selectbox("Select the mortgage term (years)", options=[20, 30], index=1)
    
    if budget > 0:
        # Calculate maximum mortgage based on citizenship and first apartment status
        if is_israeli and is_first_apartment:
            max_ltv = 0.75  # 75% loan-to-value for Israeli first-time buyers
        else:
            max_ltv = 0.50  # 50% loan-to-value for others
        
        # Since we need to solve for price iteratively, we'll estimate the maximum mortgage
        # Initial rough estimate of maximum affordable price
        fee_rate = 0.01 * 1.18 + 0.02 * 1.18  # lawyer + agent fees = 2.95%
        estimated_price = budget / (1 + fee_rate - max_ltv)
        
        # Calculate maximum mortgage based on LTV ratio
        max_mortgage_from_ltv = estimated_price * max_ltv
        
        st.success(f"Based on your profile, you can get a mortgage of up to {max_ltv*100:.0f}% of the apartment price.")
        st.info(f"With your down payment of {budget:,.0f} NIS, the estimated maximum mortgage you can take is approximately {max_mortgage_from_ltv:,.0f} NIS.\n (Since part of your downpayment will go towards fees)")
        
        # Let user choose mortgage amount
        chosen_mortgage = st.slider(
            "Choose your desired mortgage amount (NIS)", 
            min_value=0, 
            max_value=int(max_mortgage_from_ltv), 
            value=int(max_mortgage_from_ltv * 0.8),  # Default to 80% of max
            step=50000,
            help="Select how much you want to borrow. Lower amounts mean lower monthly payments."
        )
        
        if chosen_mortgage > 0:
            # Calculate monthly payment based on chosen mortgage
            if mortgage_years == 30:
                monthly_payment = (chosen_mortgage / 1000000) * 5550
            else:
                monthly_payment = (chosen_mortgage / 1000000) * 6700
            
            st.write(f"**Your estimated monthly mortgage payment: {monthly_payment:,.0f} NIS** ({mortgage_years} years)")
            
            # Now calculate the apartment price based on chosen mortgage and budget
            # We need to solve iteratively since fees depend on price
            
            # Initial estimate
            price_estimate = budget + chosen_mortgage
            
            # Iterate to find correct price including all fees
            for _ in range(10):  # Max 10 iterations
                # Calculate mortgage advisor fee
                if chosen_mortgage == 0:
                    mortgage_advisor_fee = 0
                else:
                    mortgage_advisor_fee = max(7500, chosen_mortgage * 0.01) * 1.18
                
                # Calculate purchase tax for current price estimate
                _, stamp_duty = calculate_mort_and_tax(price_estimate, is_israeli, is_first_apartment, chosen_mortgage)
                if is_oleh and is_first_apartment:
                    stamp_duty = calc_purchase_tax_oleh(price_estimate)

                
                # Calculate total fees
                lawyer_fee = price_estimate * 0.01 * 1.18
                agent_fee = price_estimate * 0.015 * 1.18
                total_fees = lawyer_fee + agent_fee + mortgage_advisor_fee + stamp_duty
                
                # Calculate new price estimate
                new_price = budget + chosen_mortgage + total_fees
                
                # Check convergence
                if abs(new_price - price_estimate) < 1000:  # Converged within 1000 NIS
                    break
                
                price_estimate = new_price
            
            price = price_estimate
            
            # Verify that the chosen mortgage doesn't exceed LTV limits
            actual_ltv = chosen_mortgage / price
            if actual_ltv > max_ltv:
                st.error(f"Warning: Your chosen mortgage exceeds the maximum allowed ({max_ltv*100:.0f}% of apartment price). Please reduce the mortgage amount.")
            else:
                # Store data in session state
                st.session_state.unknown_data = {
                    'budget': budget,
                    'is_israeli': is_israeli,
                    'is_first_apartment': is_first_apartment,
                    'is_oleh': is_oleh,                 # <— add this
                    'mortgage_years': mortgage_years,
                    'chosen_mortgage': chosen_mortgage,
                    'monthly_payment': monthly_payment,
                    'price': price,
                    'lawyer_fee': lawyer_fee,
                    'agent_fee': agent_fee,
                    'mortgage_advisor_fee': mortgage_advisor_fee,
                    'stamp_duty': stamp_duty,
                    'total_fees': total_fees,
                    'max_ltv': max_ltv
                }

                st.success(f"✅ **Summary:**")
                st.write(f"• Maximum apartment price you can afford: **{price:,.0f} NIS**")
                st.write(f"• Your down payment: **{budget:,.0f} NIS**")
                st.write(f"• Your chosen mortgage: **{chosen_mortgage:,.0f} NIS**")
                st.write(f"• Monthly mortgage payment: **{monthly_payment:,.0f} NIS**")
                st.write(f"• Loan-to-value ratio: **{actual_ltv*100:.1f}%**")
        
    else:
        st.warning("Please enter your down payment to see calculations.") 
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Home", use_container_width=True):
            go("home")
    with col2:
        if st.button("Continue: Detailed Information ➡️", use_container_width=True):
            go("unknown_details")

# --- UNKNOWN DETAILS PAGE ---
elif st.session_state.page == "unknown_details":
    st.title("🤔 Budget Analysis Details")
    
    # Check if we have the basic data
    if 'unknown_data' not in st.session_state:
        st.error("Please complete the budget basics first.")
        if st.button("⬅️ Go to Budget Basics", use_container_width=True):
            go("unknown_basics")
    else:
        data = st.session_state.unknown_data
        
        st.success("**Your Apartment Deal Summary:**")
        st.write(f"• Maximum apartment price you can afford: **{data['price']:,.0f} NIS**")
        st.write(f"• Your down payment: **{data['budget']:,.0f} NIS**")
        st.write(f"• Your chosen mortgage: **{data['chosen_mortgage']:,.0f} NIS**")
        st.write(f"• Monthly mortgage payment: **{data['monthly_payment']:,.0f} NIS** ({data['mortgage_years']} years)")
        st.write(f"• Loan-to-value (of property) ratio: **{(data['chosen_mortgage']/data['price'])*100:.1f}%**")
        
        # Show breakdown of all costs
        st.subheader("💰 Complete Cost Breakdown:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Purchase Costs:**")
            st.write(f"• Apartment price: {data['price']:,.0f} NIS")
            st.write(f"• Purchase tax: {data['stamp_duty']:,.0f} NIS")
            
            st.write("**Professional Fees:**")
            st.write(f"• Lawyer fee: {data['lawyer_fee']:,.0f} NIS")
            st.write(f"• Agent fee: {data['agent_fee']:,.0f} NIS")
            st.write(f"• Mortgage advisor fee: {data['mortgage_advisor_fee']:,.0f} NIS")
        
        with col2:
            st.write("**Financing:**")
            st.write(f"• Your down payment: {data['budget']:,.0f} NIS")
            st.write(f"• Mortgage amount: {data['chosen_mortgage']:,.0f} NIS")
            st.write(f"• Monthly payment: {data['monthly_payment']:,.0f} NIS")
        
        st.write("---")
        st.write(f"**Total fees: {data['total_fees']:,.0f} NIS**")
        
        # Verify the equation
        verification = data['budget'] + data['chosen_mortgage'] + data['total_fees']
        st.write(f"**Verification:** Down payment ({data['budget']:,.0f}) + Mortgage ({data['chosen_mortgage']:,.0f}) + Total Fees ({data['total_fees']:,.0f}) = {verification:,.0f} NIS")
        st.write(f"This should cover the apartment price: {data['price']:,.0f} NIS ✓" if abs(verification - data['price']) < 1000 else "⚠️ Calculation mismatch")
        
        # Download summary button
        download_summary = st.button("📄 Download Summary as Excel", use_container_width=True)
        if download_summary:
            summary_data = {
                "Item": [
                    "Apartment Price", 
                    "Down Payment", 
                    "Mortgage Amount", 
                    "Purchase Tax", 
                    "Agent Fee", 
                    "Lawyer Fee", 
                    "Mortgage Advisor Fee", 
                    "Total Additional Costs", 
                    "Total Cash Needed", 
                    f"Monthly Mortgage Payment ({data['mortgage_years']} years)"
                ],
                "Amount (NIS)": [
                    data['price'], 
                    data['budget'], 
                    data['chosen_mortgage'], 
                    data['stamp_duty'], 
                    data['agent_fee'], 
                    data['lawyer_fee'], 
                    data['mortgage_advisor_fee'], 
                    data['total_fees'], 
                    total_cash_needed, 
                    data['monthly_payment']
                ]
            }
            df_summary = pd.DataFrame(summary_data)
            towrite = BytesIO()
            df_summary.to_excel(towrite, index=False, sheet_name="Apartment Budget Analysis")
            towrite.seek(0)
            st.download_button(
                label="Click to Download Excel File", 
                data=towrite, 
                file_name="apartment_budget_analysis.xlsx", 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Budget Basics", use_container_width=True):
                go("unknown_basics")
        with col2:
            if st.button("🏠 Start New Calculation", use_container_width=True):
                # Clear session state and go home
                if 'unknown_data' in st.session_state:
                    del st.session_state.unknown_data
                go("home")