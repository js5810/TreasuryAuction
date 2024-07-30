import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random
import pandas as pd
import glob
import requests
from utils import *
import plotly.graph_objects as go
from datetime import datetime

class TreasuryAuction:

    def __init__(self):
        pass

    def random_user_agent(self) -> str:
        """Give a random user agent from the list to include in request"""
        with open("../metadata/Chrome.txt", "r") as f:
            user_agents = [line.strip() for line in f]
        user_agent = random.choice(user_agents)
        return user_agent

    def download_tables(self) -> None:
        """Navigates through Treasury website to gather data"""
        user_agent = self.random_user_agent()
        chrome_options = Options()
        chrome_options.add_argument(f"--user-agent={user_agent}")
        driver = uc.Chrome(options=chrome_options)
        driver.get("https://www.treasurydirect.gov/auctions/auction-query/")

        FIRST_PAGE = 1
        LAST_PAGE = 102
        for page_num in range(FIRST_PAGE, LAST_PAGE + 1):
            try:
                page_box = driver.find_element(By.CSS_SELECTOR, "input[type='text'][style='height:100%; box-sizing: border-box; text-align: right; width: 36px;'][tabindex='116'].jqx-input.jqx-input-td-2020.jqx-widget-content.jqx-widget-content-td-2020.jqx-grid-pager-input.jqx-grid-pager-input-td-2020.jqx-rc-all.jqx-rc-all-td-2020")
                page_box.clear()
                page_box.send_keys(str(page_num))
                page_box.send_keys(Keys.RETURN)
                time.sleep(2)
                download_button = driver.find_element(By.CSS_SELECTOR, "input[type='button'][value='CSV'][id='csvExport'][role='button'].jqx-rc-all")
                download_button.send_keys(Keys.RETURN)
                time.sleep(2)
            except:
                driver.quit()

    def combine_tables(self) -> None:
        """Merge all data into one large table"""
        files = glob.glob("../data/*.csv")
        df_list = []
        for file in files:
            df = pd.read_csv(file, index_col=False)
            df_list.append(df)

        combined_df = pd.concat(df_list, axis=0, ignore_index=False)
        combined_df.sort_values(by="Auction Date", inplace=True)
        combined_df.dropna(subset="Price per $100", inplace=True)
        #combined_df.to_csv("combined_data.csv", index=False)
    
    def get_all_CUSIP(self, term: str) -> list[str]:
        """Extract all CUSIP of any debt security ever sold"""
        df = pd.read_csv("../data/combined_table.csv")
        return [cusip for cusip in df[df["Security Term"] == term]["CUSIP"]]  # still need to distinugish TIPS

    def calculate_YTM(self, auction: dict) -> float:
        """Back-engineer the auction's Yield to Maturity from price, coupon rate, and time to maturity given the price (per 100 USD)"""
        security_type = auction["security_type"]
        price = auction["price"]
        coupon_rate = auction["coupon_rate"] / 100  # convert from percentage
        payment_count = auction["payment_count"]
        
        if security_type == "Bill":
            return
        else:
            return yield_bsta(coupon_rate, payment_count, price)
    
    def auction_data(self, cusip: str, tips: str) -> dict[dict]:
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
                if auction["tips"] != tips:
                    return {}
                auction_date = auction["auctionDate"]
                security_type = auction["securityType"]
                price_per_100 = float(auction["pricePer100"])
                coupon_rate = float(auction["interestRate"])  # treasury's API calls coupon rate the interest rate
                payment_count = count_payments(auction["securityTerm"]) # compute how many payments you receive
                print(auction_date, security_type, price_per_100, coupon_rate, payment_count)
                print("clear")
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

    def create_graph(self, term: str, tips: str) -> float:
        """Make a time series of yield for the term (10-Year, 30-Year, etc.) and tips (Yes or No)"""
        cusip_list = self.get_all_CUSIP(term)
        date_list = []
        ytm_list = []
        low_list = []
        high_list = []
        for cusip in cusip_list:
            all_auctions = self.auction_data(cusip, tips)
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
        print(df)

        lines_list = [
            go.Scatter(name="Auction Yield",
                       x=df["date"],
                       y=df["ytm"],
                       mode="lines",
                       line=dict(color='rgb(31, 119, 180)')),
            go.Scatter(name="lower bound",
                       x=df["date"],
                       y=df["low"],
                       marker=dict(color="#444"),
                       line=dict(width=0),
                       mode='lines',
                       fillcolor='rgba(68, 68, 68, 0.3)',
                       fill='tonexty'),
            go.Scatter(name="upper bound",
                       x=df["date"],
                       y=df["high"],
                       marker=dict(color="#444"),
                       line=dict(width=0),
                       mode='lines',
                       fillcolor='rgba(68, 68, 68, 0.3)',
                       fill='tonexty')
        ]

        lines_list = market_yield_added(lines_list, tips)

        fig = go.Figure(lines_list)
        fig.update_layout(title=f"Auction Participant's Demand for Yield Over Time",
                      title_x=0.5,
                      xaxis_title="Time",
                      yaxis_title=f"Yield To Maturity",
                      legend_title="Tickers")
        fig.show()