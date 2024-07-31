import re
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go


def price_for_yield(c: float, p: float, r: float) -> float:
    """For coupon paying notes/bonds: given the YTM, compute the present value (price) of the note/bond"""
    FACE_VALUE = 100
    return 0.99*((FACE_VALUE/2 * c) * ( (1-pow(1/(1+r), 0.5*p))/(pow(1+r, 0.5)-1) ) + FACE_VALUE/pow(1+r, 0.5*p))
    
    #return (FACE_VALUE * c) * ( (1-pow(1/(1+0.5*r), p))/(r) ) + FACE_VALUE/pow(1+0.5*r, p)


def yield_bsta(coupon_rate, payment_count, target_price):
    """For coupon paying notes/bonds: find the YTM that gives the price by using 'Binary Search The Answer' technique, basically guessing the yield and readjusting as appropriate many times"""
    low, high = 0.0, 1.0
    while abs(low - high) > 1e-15:
        mid = (low + high) / 2
        curr_price = price_for_yield(coupon_rate, payment_count, mid)
        if curr_price < target_price:
            high = mid
        elif curr_price > target_price:
            low = mid
        else:
            break
    return low


def count_payments(term_string: str, is_bill: bool) -> int:
    """For coupon paying notes/bonds: gives number of coupon payments for note or bond
       For zero coupon, discounted bills: find number of days until payment of face value"""
    pattern = r'(?P<years>\d+)-Year|(?P<months>\d+)-Month|(?P<weeks>\d+)-Week|(?P<days>\d+)-Day' # regex pattern to match "x-Year", "x-Month", "x-Week", "x-Day"
    matches = re.finditer(pattern, term_string)
    times = {"Year": 0, "Month": 0, "Week": 0, "Day": 0}
    for match in matches:
        if match.group("years"):
            times["Year"] = int(match.group("years"))
        if match.group("months"):
            times["Month"] = int(match.group("months"))
        if match.group("weeks"):
            times["Week"] = int(match.group("weeks"))
        if match.group("days"):
            times["Day"] = int(match.group("days"))
    if is_bill:
        return 365*times["Year"] + 31*times["Month"] + 7*times["Week"] + times["Day"]
    else:
        return 2*times["Year"] + (times["Month"] // 6)
    