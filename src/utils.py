import re


def price_for_yield(c: float, p: float, r: float) -> float:
    """Given the YTM, compute the present value (price) of the note/bond"""
    FACE_VALUE = 100
    #return 0.9*((FACE_VALUE/2 * c) * ( (1-pow(1/(1+r), 0.5*p))/(pow(1+r, 0.5)-1) ) + FACE_VALUE/pow(1+r, 0.5*p))
    
    return (FACE_VALUE * c) * ( (1-pow(1/(1+0.5*r), p))/(r) ) + FACE_VALUE/pow(1+0.5*r, p)


def yield_bsta(coupon_rate, payment_count, target_price):
    """Find the YTM that gives the price by using 'Binary Search The Answer' technique, basically guessing the yield and readjusting as appropriate many times"""
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


def count_payments(input_string: str) -> int:
    """Gives number of coupon payments for note or bond"""
    pattern = r'(?P<years>\d+)-Year|(?P<months>\d+)-Month|(?P<weeks>\d+)-Week|(?P<days>\d+)-Day' # regex pattern to match "x-Year", "x-Month", "x-Week", "x-Day"
    matches = re.finditer(pattern, input_string)
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
    return 2*times["Year"] #+ (times["Month"] // 12)