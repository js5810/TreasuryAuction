# TreasuryAuction Data Analyzer

![alt text](https://github.com/js5810/TreasuryAuction/blob/main/metadata/Treasury_Auction_Demo.gif)

This is useful because:
* the official TreasuryDirect website does not readily provide detailed data on auctions for new and re-opened US debt securities
* only the highest and lowest bids for the rate are shown
* API is missing many fields and only show 250; nowhere near all auctions
* more important data such as the actual YTM determined by the auction are scattered throughout the website on interactive tables and PDF documents
* hard to quickly summarize the auction participants' outlook on spot interest rates

This program:
* automatically gathers the latest auction results of US treasury bills, notes, and bonds and creates useful visualizations
* constantly checks for any new auction data and will produce a visual report as soon as the most recent auction is posted

In short, the program taps into auctions as a new way of gauging market participants' outlook on interest rates which can be helpful to consider in conjunction with the actual yield curve which is derived from the prices of the treasury instruments trading in the open market.

## How New Treasury Bills, Notes, and Bonds are Issued
The Department of the Treasury issues new debt securities by offering them for an auction in which anyone can submit bids for the yield to maturity (YTM) that they are willing to accept. Thus, these YTM bids are what the participants are demanding as a rate of return for purchasing the treasury bond. One can also submit non-competitive bids which indicates that the person is willing to take any YTM and just wants to buy the desired dollar amount. The actual YTM which in turn gives the price of the bond is the lowest rate that can sell all the bonds that were being offered. For instance, there was an auction for US treasury notes with 7 years to maturity (CUSIP 91282CHJ3) where &#36;35B worth was offered. The full auction details are at https://www.treasurydirect.gov/instit/annceresult/press/preanre/2023/A_20230622_7.pdf 

This auction resulted in an initial price of 99.458207 USD per 100 USD which is at a discount to the par value because the winning YTM was larger than the coupon rate of 3.75%. Bonds that are re-opened through auction already have an assigned coupon rate. This means that the only variable needed to price the instrument is the YTM which is determined by the auction. If a completely new bond is being issued (which is the case for the treasury note above), the coupon rate has to also be decided on. The Department of Treasury fixes the coupon rate by taking the closest multiple of $\frac{1}{8}=0.125$% that is smaller than the auction's YTM. This is to make the initial price of the bond as close to par value as possible while keeping the coupon rate at a friendly number that is a multiple of 0.125.The bond price would be par value if the coupon rate was exactly equal to the YTM but the Treasury doesn't do this because they want to keep coupon rates a nice multiple. Thus, most prices will be at a discount or at par with face value. Occasionally, the price will be at a premium which means that the auction was a re-opening where the coupon rate already existed and the YTM determined by the auction ended up being smaller than the coupon rate.

## Extracting Interest Rate Insight
Now that we know how these auctions work, we can reverse engineer the auction markets' view on spot rates using the price per 100 USD. This is done by solving for the YTM variable $r$ in the discounted cash flow formula applied to the cash flows of a risk-free bond that matures in $T$ years:

$$\text{price} = \Bigg(\sum_{k=1}^{T}\frac{C}{(1+r)^k}\Bigg) + \frac{F}{(1+r)^T}$$

This is a $k$th order polynomial that can be solved with Python.
