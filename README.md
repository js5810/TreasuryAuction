# TreasuryAuction Data Analyzer

![alt text](https://github.com/js5810/TreasuryAuction/blob/main/metadata/Treasury_Auction_Demo.gif)

This is useful because:
* the official TreasuryDirect website does not readily provide detailed data on auctions for new and re-opened US debt securities
* API is missing many fields and only show 250; nowhere near all auctions
* more important data such as the actual YTM determined by the auction are scattered throughout the website on interactive tables and PDF documents
* you can quickly see that the range of bids is larger when there is uncertainty about the yield (Low rates during COVID 2020-2021)
* the range has also widened between 10Y note auctions on July 10th and August 7th, 2024 due to uncertainty caused by higher unemployment rates shortly after the Fed kept rates constant for July 2024 as well as the unwinding of Yen carry trades following BOJ's rate hike

This program:
* automatically gathers the latest auction results of US treasury bills, notes, and bonds and creates useful visualizations
* constantly checks for any new auction data and will produce an interactive graph as soon as the most recent auction is posted

In short, the program taps into auctions as a new way of gauging market participants' confidence on interest rates which can be helpful to consider in conjunction with the actual yield curve which is derived from the prices of the treasury instruments trading in the secondary market.

## How New Treasury Bills, Notes, and Bonds are Issued
The Department of the Treasury issues new debt securities by offering them for an auction in which anyone can submit bids for the yield to maturity (YTM) that they are willing to accept. Thus, these YTM bids are what the participants are demanding as a rate of return for purchasing the treasury bond. One can also submit non-competitive bids which indicates that the person is willing to take any YTM and just wants to buy the desired dollar amount. The actual YTM which in turn gives the price of the bond is the lowest rate that can sell all the bonds that were being offered. For instance, there was an auction for US treasury notes with 7 years to maturity (CUSIP 91282CHJ3) where &#36;35B worth was offered. The full auction details are at https://www.treasurydirect.gov/instit/annceresult/press/preanre/2023/A_20230622_7.pdf 

This auction resulted in an initial price of 99.458207 USD per 100 USD which is at a discount to the par value because the winning YTM was larger than the coupon rate of 3.75%. Bonds that are re-opened through auction already have an assigned coupon rate. This means that the only variable needed to price the instrument is the YTM which is determined by the auction. If a completely new bond is being issued (which is the case for the treasury note above), the coupon rate has to also be decided on. The Department of Treasury fixes the coupon rate by taking the closest multiple of $\frac{1}{8}=0.125$% that is smaller than the auction's YTM. This is to make the initial price of the bond as close to par value as possible while keeping the coupon rate at a friendly number that is a multiple of 0.125.The bond price would be par value if the coupon rate was exactly equal to the YTM but the Treasury doesn't do this because they want to keep coupon rates a nice multiple. Thus, most prices will be at a discount or at par with face value. Occasionally, the price will be at a premium which means that the auction was a re-opening where the coupon rate already existed and the YTM determined by the auction ended up being smaller than the coupon rate.

## Extracting Interest Rate Insight
Now that we know how these auctions work, we can reverse engineer the auction markets' view on spot rates using the price per 100 USD since that is the number that the Department of the Treasury provides on their website. This is done by solving for the YTM variable $r$ in the discounted cash flow formula applied to the cash flows of a risk-free bond that matures in $T$ years:

$$\text{price} = \Bigg(\sum_{k=1}^{T}\frac{C}{(1+r)^k}\Bigg) + \frac{F}{(1+r)^T}$$

Since treasury sercurities are risk-free, we do not need to account for default risk. Thus, we have a sum of terms of a geometric sequence which we can simplify as 

$$C\cdot\frac{1-\frac{1}{(1+r)^T}}{r}+\frac{F}{(1+r)^T}$$

Suppose the price per $100 is given by the Dept. of Treasury to be P. Then solving the equation boils down to a T-th degree polynomial.

$$C\cdot\frac{1-\frac{1}{(1+r)^T}}{r}+\frac{F}{(1+r)^T}=P$$

 This polynomial can be solved analytically or with the help of Python. In practice, my code actually uses the the monotonicity of the function to find the solution by empirically trying yields until the correct price is reached using a techinique called Binary Seach the Answer (BSTA). We start with a range in which the yield is contained and keep narrowing it down until we get the yield that would produce the observed security price per $100. This is much faster than solving the T-th degree polynomial and requires much less computation since it leverages binary search. The fact that the pricing formula is strictly decreasing is intuitive because we know higher yield means lower bond price. We can verify this by taking the derivative of the polynomial and seeing it is negative for all yields r.