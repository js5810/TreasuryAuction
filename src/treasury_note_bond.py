from treasury_security import TreasurySecurity
import requests
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from utils import *

class TreasuryNoteBond(TreasurySecurity):
    def __init__(self, term: str, tips: str):
        self.term = term
        self.tips = tips  # Yes or No String
    
    def calculate_YTM(self, auction: dict) -> float:
        """Back-engineer the auction's Yield to Maturity given price per 100, coupon rate, and time to maturity"""
        price = auction["price"]
        coupon_rate = auction["coupon_rate"] / 100  # convert from percentage
        payment_count = auction["payment_count"]
        return yield_bsta(coupon_rate, payment_count, price)

    def auction_data(self, cusip: str) -> dict[dict]:
        """Retrieve the price, coupon rate, and low/median/high bids for yield from all auctions that ever took place for this debt security"""
        user_agent = self.random_user_agent()
        headers = {
            "User-Agent": user_agent
        }
        TREASURY_URL = f"https://www.treasurydirect.gov/TA_WS/securities/search?cusip={cusip}&callback=?&format=json"
        response_json = requests.get(url=TREASURY_URL, headers=headers).json()

        relevant_data = {}
        for auction in response_json:  # each dictionary object is a separate auction day
            # non-negotiables:
            try:
                if auction["tips"] != self.tips:
                    return {}
                auction_date = auction["auctionDate"]
                security_type = auction["securityType"]
                price_per_100 = float(auction["pricePer100"])
                coupon_rate = float(auction["interestRate"])  # treasury's API calls coupon rate the interest rate
                payment_count = count_payments(auction["securityTerm"], False) # compute how many payments you receive
                print(auction_date, security_type, price_per_100, coupon_rate, payment_count)
            except ValueError as e:
                continue
            relevant_data[auction_date] = {}
            relevant_data[auction_date]["security_type"] = security_type
            relevant_data[auction_date]["price"] = price_per_100
            relevant_data[auction_date]["coupon_rate"] = coupon_rate
            relevant_data[auction_date]["payment_count"] = payment_count # dict containing time data

            # acceptable if it's missing:
            try:
                lowest_YTM = float(auction["lowYield"])
                relevant_data[auction_date]["low_bid"] = lowest_YTM
            except ValueError as e:
                pass
            try:
                highest_YTM = float(auction["highYield"])
                relevant_data[auction_date]["high_bid"] = highest_YTM
            except ValueError as e:
                pass
            try:
                median_YTM = float(auction["averageMedianYield"])
                relevant_data[auction_date]["median_bid"] = median_YTM
            except ValueError as e:
                pass

        return relevant_data
    

    def market_yield_added(self, fig_list: list) -> list:
        """Add graph for the secondary market yield which is just from FRED"""
        DATA_DICT = {
            "Yes": {
                "10-Year": "DFII10",
                "20-Year": "DFII20",
                "30-Year": "DFII30"
            },
            "No": {
                "10-Year": "DGS10",
                "20-Year": "DGS20",
                "30-Year": "DGS30"
            }
        }
        filename = DATA_DICT[self.tips][self.term]
        market_df = pd.read_csv(f"../data/FRED_data/{filename}.csv")
        market_df["DATE"] = market_df["DATE"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
        fig_list.append(go.Scatter(name="Secondary Market Yield",
                    x=market_df["DATE"],
                    y=market_df[filename],
                    mode="lines",
                    line=dict(color='rgb(255,69,0)')))
        return fig_list


    def create_graph(self) -> None:
        """Make interactive graph of yield bids from auction as well as secondary market yield for given term
           tips is a string Yes or No to indicate if we are considering inflation adjusted securities"""
        cusip_list = self.get_all_CUSIP(self.term)
        date_list = []
        ytm_list = []
        low_list = []
        high_list = []
        for cusip in cusip_list:
            all_auctions = self.auction_data(cusip)
            for auction_date in all_auctions:
                a = all_auctions[auction_date] # dict containing data from specific auction
                date_list.append(datetime.fromisoformat(auction_date))
                low = a["low_bid"]
                low_list.append(low)
                high = a["high_bid"]
                high_list.append(high)
                ytm = self.calculate_YTM(a) * 100 # convert back to percent
                if ytm < low:
                    ytm = low
                if ytm > high:
                    ytm = high
                ytm_list.append(ytm)

        df = pd.DataFrame(data={"date": date_list, "ytm": ytm_list, "low": low_list, "high": high_list})
        df.sort_values(by=['date'], inplace=True)
        df.reset_index(inplace=True, drop=True)

        lines_list = [
            go.Scatter(name="Auction Yield",
                    x=df["date"],
                    y=df["ytm"],
                    mode="lines",
                    line=dict(color='rgb(31, 119, 180)')),
            go.Candlestick(name="Range of Yield Bids",
                        x=df["date"],
                        low=df["low"],
                        high=df["high"],
                        open=df["ytm"],
                        close=df["ytm"])
        ]
        

        lines_list = self.market_yield_added(lines_list)

        fig = go.Figure(lines_list)
        fig.update_layout(title=f"Auction Participant's Confidence in Yield Over Time ({self.term}, TIPS: {self.tips})",
                    title_x=0.5,
                    xaxis_title="Time",
                    yaxis_title=f"Yield (%)",
                    legend_title="Types of Yield")
        fig.show()