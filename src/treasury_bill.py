from treasury_security import TreasurySecurity
import requests
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from utils import *

class TreasuryBill(TreasurySecurity):
    def __init__(self, term: str):
        self.term = term
    
    def calculate_YTM(self, auction: dict) -> float:
        """Solve for the auction's Yield to Maturity from price per 100 and time to maturity"""
        price_per_100 = auction["price"]
        num_days = auction["days_to_maturity"]
        return pow(100/price_per_100, 365 / num_days) - 1

    def auction_data(self, cusip: str) -> dict[dict]:
        """Get all auctions for bill with this cusip"""
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
                auction_date = auction["auctionDate"]
                security_type = auction["securityType"]
                price_per_100 = float(auction["pricePer100"])
                num_days = count_payments(auction["securityTerm"], True) # compute how many payments you receive
                print(auction_date, security_type, price_per_100, num_days)
            except ValueError as e:
                continue
            relevant_data[auction_date] = {}
            relevant_data[auction_date]["security_type"] = security_type
            relevant_data[auction_date]["price"] = price_per_100
            relevant_data[auction_date]["days_to_maturity"] = num_days

            # acceptable if it's missing:
            try:
                low_discount = float(auction["lowDiscountRate"]) / 100  # convert from percent
                low_yield = yield_from_discount(low_discount, num_days)
                relevant_data[auction_date]["low_bid"] = low_yield
            except ValueError as e:
                pass
            try:
                high_discount = float(auction["highDiscountRate"]) / 100  # convert from percent
                high_yield = yield_from_discount(high_discount, num_days)
                relevant_data[auction_date]["high_bid"] = high_yield
            except ValueError as e:
                pass

        return relevant_data
    
    def market_yield_added(self, fig_list: list) -> list:
        #DATA_DICT = {
        #    "13-Week": ,
        #    "26-Week": 
        #}
        market_df = pd.read_csv("../data/FRED_data/DGS10.csv")
        market_df["DATE"] = market_df["DATE"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
        fig_list.append(go.Scatter(name="Secondary Market Yield",
                    x=market_df["DATE"],
                    y=market_df["DGS10"],
                    mode="lines",
                    line=dict(color='rgb(255,69,0)')))
        return fig_list

    def create_graph(self) -> None:
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
        fig.update_layout(title=f"Auction Participant's Confidence in Yield Over Time ({self.term})",
                    title_x=0.5,
                    xaxis_title="Time",
                    yaxis_title=f"Yield (%)",
                    legend_title="Types of Yield")
        fig.show()