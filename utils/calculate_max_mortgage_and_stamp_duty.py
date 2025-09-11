

def calculate_mort_and_tax(price, is_israeli, is_first_apartment, mortgage_amount):
    """
    Calculate the maximum mortgage and stamp duty based on the deal price,
    citizenship status, first apartment status, and mortgage amount.

    Parameters:
    - price (float): The price of the apartment deal in NIS.
    - is_israeli (bool): True if the user is an Israeli citizen, False otherwise.
    - is_first_apartment (bool): True if this is the user's first apartment, False otherwise.
    - mortgage_percentage (float): The percentage of the deal price to be taken as a mortgage.

    Returns:
    - max_mortgage (float): The maximum mortgage amount in NIS.
    - stamp_duty (float): The stamp duty amount in NIS.
    """
    # The maximum mortgage is 75% of the deal price for israelis which this is their first apartment
    # and 50% for everyone else
    if is_israeli and is_first_apartment:
        max_mortgage = price * 0.75
    else:
        max_mortgage = price * 0.50

    # The stamp duty is calculated as follows: it is 8% for Israelis where this is not their first apartment
    # 8% for non Israelis.
    # For Israelis where this is their first apartment:
    #על חלק השווי שעד 1,978,745 ש"ח – לא ישולם מס
    #על חלק השווי העולה על 1,978,745 ש"ח ועד 2,347,040 ש"ח – 3.5%
    #על חלק השווי העולה על 2,347,040 ש"ח ועד 6,055,070 ש"ח – 5%
    #על חלק השווי העולה על 6,055,070 ש"ח ועד 20,183,565 ש"ח – 8%
    #על חלק השווי העולה על 20,183,565 ש"ח – 10%

    if is_israeli and is_first_apartment:
        if price <= 1978745:
            stamp_duty = 0
        elif price <= 2347040:
            stamp_duty = (price - 1978745) * 0.035
        elif price <= 6055070:
            stamp_duty = (2347040 - 1978745) * 0.035 + (price - 2347040) * 0.05
        elif price <= 20183565:
            stamp_duty = (2347040 - 1978745) * 0.035 + (6055070 - 2347040) * 0.05 + (price - 6055070) * 0.08
        else:
            stamp_duty = (2347040 - 1978745) * 0.035 + (6055070 - 2347040) * 0.05 + (20183565 - 6055070) * 0.08 + (price - 20183565) * 0.10

    else:
        stamp_duty = price * 0.08
    return max_mortgage, stamp_duty