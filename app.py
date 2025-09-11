# app.py
import streamlit as st
from utils.calculate_max_mortgage_and_stamp_duty import calculate_mort_and_tax
import pandas as pd
from io import BytesIO
st.set_page_config(page_title="Apartment Journey", page_icon="🏠")

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

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ I know the deal I'm interested in", use_container_width=True):
            go("known")
    with col2:
        if st.button("🤔 I do not", use_container_width=True):
            go("unknown")

# --- KNOWN DEAL PAGE ---
elif st.session_state.page == "known":
    st.title("✅ I already know the deal")
    # Create a few tabs to collect the details of the deal, the first tab will focus on the price mortgage and tax details
    # the second tab will focus on the expenses such as lawyer fee, agent fee and יועץ משכנתא fee
    # The third tab will focus on the mortgage
    tab1, tab2, tab3, tab4 = st.tabs(["Deal Basics", "Additional Expenses", "Mortgage Details", "Summary"])
    with tab1:
        st.write("Great! Let's collect the basic details of your chosen apartment deal.")
        # The user will enter the price of the deal he was offered in NIS
        price = st.number_input("Enter the price of the deal (NIS)", min_value=0)
        # The user will enter wether he is an Israeli citizen or not
        is_israeli = st.checkbox("I am an Israeli citizen")
        # The user will enter wether this is his first apartment or not
        is_first_apartment = st.checkbox("This is my first apartment")
        # The user will enter the amount IN nis he wants to take as a mortgage
        mortgage_amount = st.number_input("Enter the amount you want to take as a mortgage (NIS)", min_value=0)
        
        mortgage, stamp_duty = calculate_mort_and_tax(price, is_israeli, is_first_apartment, mortgage_amount)
        if mortgage_amount > mortgage:
            st.error(f"The maximum mortgage you can take is {mortgage:,.0f} NIS. Please adjust your desired mortgage amount.")
        else:
            st.success(f"The maximum mortgage you can take is {mortgage:,.0f} NIS.")
            st.info(f"The stamp duty for this deal is {stamp_duty:,.0f} NIS.")
        #Tell user to go to additional expenses tab
        st.write("Please proceed to the 'Additional Expenses' tab to enter details about other costs associated with your deal.")

# ...existing code...
    with tab2:
        st.write("Now, let's gather information about any additional expenses related to your apartment deal.")
        
        # Agent fee section
        st.subheader("Agent Fee")
        knows_agent_fee = st.checkbox("I know the agent fee")
        
        if knows_agent_fee:
            # The user inputs the agent fee in pct, or nis if he prefers
            agent_fee_pct = st.number_input("Enter the agent fee percentage (%)", min_value=0.0, max_value=100.0, step=0.1)
            agent_fee_nis = st.number_input("Or enter the agent fee amount (NIS)", min_value=0)
            if agent_fee_pct > 0:
                agent_fee = price * (agent_fee_pct / 100)
                # add vat at 18%
                agent_fee = agent_fee * 1.18
                st.info(f"The agent fee based on the percentage is {agent_fee:,.0f} NIS. (Including 18% VAT)")
            elif agent_fee_nis > 0:
                agent_fee = agent_fee_nis * 1.18
                st.info(f"Agent fee: {agent_fee:,.0f} NIS. (Including 18% VAT)")
            else:
                st.warning("Please enter either a percentage or amount for the agent fee.")
                agent_fee = 0
        else:
            # Default to 1.5% plus VAT
            agent_fee = price * 0.015 * 1.18
            st.info(f"Using default agent fee: {agent_fee:,.0f} NIS (1.5% + 18% VAT)")
        
        # Lawyer fee section
        st.subheader("Lawyer Fee")
        knows_lawyer_fee = st.checkbox("I know the lawyer fee")
        
        if knows_lawyer_fee:
            # The user inputs the lawyer fee in pct, or nis if he prefers, USUALLY 1%
            lawyer_fee_pct = st.number_input("Enter the lawyer fee percentage (%)", min_value=0.0, max_value=100.0, step=0.1)
            lawyer_fee_nis = st.number_input("Or enter the lawyer fee amount (NIS)", min_value=0)
            if lawyer_fee_pct > 0:
                lawyer_fee = price * (lawyer_fee_pct / 100)
                # add vat at 18%
                lawyer_fee = lawyer_fee * 1.18
                st.info(f"The lawyer fee based on the percentage is {lawyer_fee:,.0f} NIS. (Including 18% VAT)")
            elif lawyer_fee_nis > 0:
                lawyer_fee = lawyer_fee_nis * 1.18
                st.info(f"Lawyer fee: {lawyer_fee:,.0f} NIS. (Including 18% VAT)")
            else:
                st.warning("Please enter either a percentage or amount for the lawyer fee.")
                lawyer_fee = 0
        else:
            # If the user does not know default to 1% of the price
            lawyer_fee = price * 0.01 * 1.18
            st.info(f"Using default lawyer fee: {lawyer_fee:,.0f} NIS (1% + 18% VAT)")

        # Mortgage advisor fee section
        st.subheader("Mortgage Advisor Fee")
        knows_mortgage_advisor_fee = st.checkbox("I know the mortgage advisor fee")
        
        if knows_mortgage_advisor_fee:
            # THE user inputs the יועץ משכנתא fee in pct, or nis if he prefers, usually 1% of the mortgage amount minimum of 7500 nis
            mortgage_advisor_fee_pct = st.number_input("Enter the mortgage advisor fee percentage (%)", min_value=0.0, max_value=100.0, step=0.1)
            mortgage_advisor_fee_nis = st.number_input("Or enter the mortgage advisor fee amount (NIS)", min_value=0)
            if mortgage_advisor_fee_pct > 0:
                mortgage_advisor_fee = mortgage_amount * (mortgage_advisor_fee_pct / 100)
                # add vat at 18%
                mortgage_advisor_fee = mortgage_advisor_fee * 1.18
                st.info(f"The mortgage advisor fee based on the percentage is {mortgage_advisor_fee:,.0f} NIS. (Including 18% VAT)")
            elif mortgage_advisor_fee_nis > 0:
                mortgage_advisor_fee = mortgage_advisor_fee_nis * 1.18
                st.info(f"Mortgage advisor fee: {mortgage_advisor_fee:,.0f} NIS. (Including 18% VAT)")
            else:
                st.warning("Please enter either a percentage or amount for the mortgage advisor fee.")
                mortgage_advisor_fee = 0
        else:
            # If the user does not know default to 7500 nis or 1% of the mortgage amount whichever is higher
            mortgage_advisor_fee = max(7500, mortgage_amount * 0.01) * 1.18
            st.info(f"Using default mortgage advisor fee: {mortgage_advisor_fee:,.0f} NIS (min. 7500 NIS or 1% + 18% VAT)")
        # Tell user to go to mortgage details tab
        st.write("Please proceed to the 'Mortgage Details' tab to enter details about your mortgage.")

    with tab3:
        st.write("Finally, let's review the details of your mortgage.")
        st.write(f"You have chosen to take a mortgage of {mortgage_amount:,.0f} NIS.")
        # Ask the user whether he wants the mortgage is for 20 or 30 years
        mortgage_years = st.selectbox("Select the mortgage term (years)", options=[20, 30], index=0)
        if mortgage_years == 30:
            # The monthly payment is 5,550 for every 1,000,000 nis borrowed
            monthly_payment = (mortgage_amount / 1000000) * 5550
        else:
            # 6,700 for every 1,000,000 nis borrowed
            monthly_payment = (mortgage_amount / 1000000) * 6700
        st.write(f"Your estimated monthly mortgage payment is {monthly_payment:,.0f} NIS.")
        st.write("Please proceed to the 'Summary' tab to review all details of your apartment deal.")
    with tab4:
        st.write("Here's a summary of your apartment deal and associated costs:")
        st.write(f"• Apartment Price: {price:,.0f} NIS")
        st.write(f"• Mortgage Amount: {mortgage_amount:,.0f} NIS")
        st.write(f"• Stamp Duty: {stamp_duty:,.0f} NIS")
        st.write(f"• Agent Fee: {agent_fee:,.0f} NIS")
        st.write(f"• Lawyer Fee: {lawyer_fee:,.0f} NIS")
        st.write(f"• Mortgage Advisor Fee: {mortgage_advisor_fee:,.0f} NIS")
        total_costs = stamp_duty + agent_fee + lawyer_fee + mortgage_advisor_fee
        st.write(f"• Total Additional Costs: {total_costs:,.0f} NIS")
        total_investment = price - mortgage_amount + total_costs
        st.write(f"• Total Cash Investment (Price - Mortgage + Additional Costs): {total_investment:,.0f} NIS")
        if mortgage_years == 30:
            monthly_payment = (mortgage_amount / 1000000) * 5550
        else:
            monthly_payment = (mortgage_amount / 1000000) * 6700
        st.write(f"• Estimated Monthly Mortgage Payment ({mortgage_years} years): {monthly_payment:,.0f} NIS")
        download_summary = st.button("Download Summary as Excel")
        if download_summary:
            summary_data = {
                "Item": ["Apartment Price", "Mortgage Amount", "Stamp Duty", "Agent Fee", "Lawyer Fee", "Mortgage Advisor Fee", "Total Additional Costs", "Total Cash Investment", f"Estimated Monthly Mortgage Payment ({mortgage_years} years)"],
                "Amount (NIS)": [price, mortgage_amount, stamp_duty, agent_fee, lawyer_fee, mortgage_advisor_fee, total_costs, total_investment, monthly_payment]
            }
            df_summary = pd.DataFrame(summary_data)
            towrite = BytesIO()
            df_summary.to_excel(towrite, index=False, sheet_name="Apartment Deal Summary")
            towrite.seek(0)
            st.download_button(label="Click to Download", data=towrite, file_name="apartment_deal_summary.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    if st.button("⬅️ Back", use_container_width=True):
        go("home")

# --- UNKNOWN DEAL PAGE ---
elif st.session_state.page == "unknown":
    st.title("🤔 Help me decide")
    tab1, tab2 = st.tabs(["Basics", "Information"])
    with tab1:
        st.write("Let's start with some basic information to help you find the right apartment deal.")
        # The user will enter his budget in NIS
        budget = st.number_input("Enter your budget (NIS)", min_value=0)
        # The user will enter wether he is an Israeli citizen or not
        is_israeli = st.checkbox("I am an Israeli citizen")
        # The user will enter wether this is his first apartment or not
        is_first_apartment = st.checkbox("This is my first apartment")
        # The user will enter the max amount he wants to return as a mortgage each month
        max_monthly_payment = st.number_input("Enter the maximum monthly mortgage payment you can afford (NIS)", min_value=0)
        # We will calculate the maximum mortgage he can take based on the max monthly payment and the years
        mortgage_years = st.selectbox("Select the mortgage term (years)", options=[20, 30], index=0)
        # The agent fee, lawyer fee and יועץ משכנתא fee are all dependent on the price - so we will calculate the price
        # price = (budget - lawyer_fee - agent_fee - mortgage_advisor_fee - stamp_duty) + mortgage_amount
        # We will assume the user will take the maximum mortgage he can get as long as the returned montly payment is less than the max he can afford
        # lawyer fee = price * 0.01 * 1.18, agent fee = price * 0.015 * 1.18, mortgage_advisor_fee = max(7500, mortgage_amount * 0.01) * 1.18
        # stamp_duty varies based on price, citizenship, and first apartment status
        # mortgage_amount = min((max_monthly_payment / 5550) * 1000000 if mortgage_years == 30 else (max_monthly_payment / 6700) * 1000000 , 0.75 * price if is_israeli and is_first_apartment else 0.50 * price)
        # We will solve the equation to get the price
        
        if budget > 0 and max_monthly_payment > 0:
            # Calculate maximum mortgage based on monthly payment capacity
            if mortgage_years == 30:
                max_mortgage_from_payment = (max_monthly_payment / 5550) * 1000000
            else:
                max_mortgage_from_payment = (max_monthly_payment / 6700) * 1000000
            
            # Since stamp duty depends on price and we need to solve iteratively, 
            # we'll use an iterative approach to find the correct price
            
            # Initial estimate (ignoring stamp duty for first iteration)
            fee_rate = 0.01 * 1.18 + 0.015 * 1.18  # lawyer + agent fees = 2.95%
            
            if is_israeli and is_first_apartment:
                # Start with an initial price estimate
                price_estimate = budget / (1 + fee_rate - 0.75)  # Rough estimate
                
                # Iterate to find correct price including stamp duty
                for _ in range(10):  # Max 10 iterations should be enough
                    # Calculate mortgage amount based on current price estimate
                    max_mortgage_from_ltv = 0.75 * price_estimate
                    max_mortgage = min(max_mortgage_from_payment, max_mortgage_from_ltv)
                    
                    # Calculate mortgage advisor fee
                    mortgage_advisor_fee = max(7500, max_mortgage * 0.01) * 1.18
                    
                    # Calculate stamp duty for current price estimate
                    _, stamp_duty = calculate_mort_and_tax(price_estimate, is_israeli, is_first_apartment, max_mortgage)
                    
                    # Calculate total fees
                    lawyer_fee = price_estimate * 0.01 * 1.18
                    agent_fee = price_estimate * 0.015 * 1.18
                    total_fees = lawyer_fee + agent_fee + mortgage_advisor_fee + stamp_duty
                    
                    # Calculate new price estimate
                    new_price = budget + max_mortgage - total_fees
                    
                    # Check convergence
                    if abs(new_price - price_estimate) < 1000:  # Converged within 1000 NIS
                        break
                    
                    price_estimate = new_price
                
                price = price_estimate
                
            else:
                # Non-Israeli or non-first apartment (50% LTV)
                price_estimate = budget / (1 + fee_rate - 0.50)  # Rough estimate
                
                # Iterate to find correct price including stamp duty
                for _ in range(10):
                    # Calculate mortgage amount based on current price estimate
                    max_mortgage_from_ltv = 0.50 * price_estimate
                    max_mortgage = min(max_mortgage_from_payment, max_mortgage_from_ltv)
                    
                    # Calculate mortgage advisor fee
                    mortgage_advisor_fee = max(7500, max_mortgage * 0.01) * 1.18
                    
                    # Calculate stamp duty for current price estimate
                    _, stamp_duty = calculate_mort_and_tax(price_estimate, is_israeli, is_first_apartment, max_mortgage)
                    
                    # Calculate total fees
                    lawyer_fee = price_estimate * 0.01 * 1.18
                    agent_fee = price_estimate * 0.015 * 1.18
                    total_fees = lawyer_fee + agent_fee + mortgage_advisor_fee + stamp_duty
                    
                    # Calculate new price estimate
                    new_price = budget + max_mortgage - total_fees
                    
                    # Check convergence
                    if abs(new_price - price_estimate) < 1000:
                        break
                    
                    price_estimate = new_price
                
                price = price_estimate
            
            # Final calculations with converged price
            if is_israeli and is_first_apartment:
                max_mortgage = min(max_mortgage_from_payment, 0.75 * price)
            else:
                max_mortgage = min(max_mortgage_from_payment, 0.50 * price)
            
            # Calculate final fees and stamp duty
            lawyer_fee = price * 0.01 * 1.18
            agent_fee = price * 0.015 * 1.18
            mortgage_advisor_fee = max(7500, max_mortgage * 0.01) * 1.18
            _, stamp_duty = calculate_mort_and_tax(price, is_israeli, is_first_apartment, max_mortgage)
            total_fees = lawyer_fee + agent_fee + mortgage_advisor_fee + stamp_duty
            
            st.info(f"Based on your budget of {budget:,.0f} NIS and maximum monthly payment of {max_monthly_payment:,.0f} NIS:")
            st.success(f"• Maximum apartment price you can afford: {price:,.0f} NIS")
            st.success(f"• Maximum mortgage you can take: {max_mortgage:,.0f} NIS")
            st.success(f"• Your cash investment: {budget:,.0f} NIS")
            
        else:
            st.warning("Please enter your budget and maximum monthly payment to see calculations.") 
        
        # Tell user to go to information tab
        st.write("Please proceed to the 'Information' tab to review the details of your potential apartment deal.")

    with tab2:
        # Make sure price and max_mortgage are defined
        if 'price' not in locals() or 'max_mortgage' not in locals():
            st.warning("Please complete the 'Basics' tab first.")
        else: 
            st.info(f"Based on your budget of {budget:,.0f} NIS and maximum monthly payment of {max_monthly_payment:,.0f} NIS:")
            st.success(f"• Maximum apartment price you can afford: {price:,.0f} NIS")
            st.success(f"• Maximum mortgage you can take: {max_mortgage:,.0f} NIS")
            st.success(f"• Your cash investment: {budget:,.0f} NIS")
            
            # Show breakdown of costs
            st.subheader("Cost Breakdown:")
            st.write(f"• Apartment price: {price:,.0f} NIS")
            st.write(f"• Mortgage: {max_mortgage:,.0f} NIS")
            st.write(f"• Stamp duty: {stamp_duty:,.0f} NIS")
            st.write(f"• Lawyer fee: {lawyer_fee:,.0f} NIS")
            st.write(f"• Agent fee: {agent_fee:,.0f} NIS")
            st.write(f"• Mortgage advisor fee: {mortgage_advisor_fee:,.0f} NIS")
            st.write(f"• **Total fees: {total_fees:,.0f} NIS**")
            
            # Calculate actual monthly payment
            if mortgage_years == 30:
                actual_monthly_payment = (max_mortgage / 1000000) * 5550
            else:
                actual_monthly_payment = (max_mortgage / 1000000) * 6700
            st.info(f"• Your actual monthly mortgage payment: {actual_monthly_payment:,.0f} NIS")
            
            # Verify the equation
            verification = budget + max_mortgage - total_fees
            st.write(f"Verification: Budget ({budget:,.0f}) + Mortgage ({max_mortgage:,.0f}) - Total Fees ({total_fees:,.0f}) = {verification:,.0f} NIS (should equal price: {price:,.0f} NIS)")
            # Download summary button
            download_summary = st.button("Download Summary as Excel")
            if download_summary:
                summary_data = {
                    "Item": ["Apartment Price", "Mortgage Amount", "Stamp Duty", "Agent Fee", "Lawyer Fee", "Mortgage Advisor Fee", "Total Additional Costs", "Total Cash Investment", f"Estimated Monthly Mortgage Payment ({mortgage_years} years)"],
                    "Amount (NIS)": [price, max_mortgage, stamp_duty, agent_fee, lawyer_fee, mortgage_advisor_fee, total_fees, budget, actual_monthly_payment]
                }
                df_summary = pd.DataFrame(summary_data)
                towrite = BytesIO()
                df_summary.to_excel(towrite, index=False, sheet_name="Apartment Deal Summary")
                towrite.seek(0)
                st.download_button(label="Click to Download", data=towrite, file_name="apartment_deal_summary.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        