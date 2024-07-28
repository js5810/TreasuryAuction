# TreasuryAuction Data Analyzer
This is useful because:
* the official TreasuryDirect website does not readily provide detailed data on auctions for new and re-opened US debt securities
* only the highest and lowest bids for the rate are shown
* more important data such as the actual YTM determined by the auction are scattered throughout the website on interactive tables and PDF documents
* hard to quickly summarize the auction participants' outlook on spot interest rates

This program:
* automatically gathers the latest auction results of US treasury bills, notes, and bonds and creates useful visualizations
* constantly checks for any new auction data and will produce a visual report as soon as the most recent auction is posted

In short, the program taps into auctions as a new way of gauging market participants' outlook on interest rates which can be helpful to consider in conjunction with the actual yield curve which is derived from the prices of the treasury instruments trading in the open market.

## How New Treasury Bills, Notes, and Bonds are Issued
The Department of the Treasury issues new debt securities by offering them for an auction in which anyone can submit bids for the yield to maturity (YTM) that they are willing to accept. One can also submit non-competitive bids which indicates that the person is willing to take any YTM and just wants to buy the desired dollar amount. The actual YTM which in turn gives the price of the bond is the lowest rate that can sell all the bonds that were being offered. For instance, there was an auction for US treasury notes with 7 years to maturity (CUSIP 91282CHJ3) where 35B USD worth was offered. The auction resulted in an initial price of \$99.458207 per \$100 which is at a discount to the par value because the winning YTM was larger than the coupon rate. Bonds that are re-opened through auction already have an assigned coupon rate. This means that the only variable needed to price the instrument is the YTM which is determined by the auction. If a completely new bond is being issued (which is the case for the treasury note above), the coupon rate has to also be decided on. The Department of Treasury fixes the coupon rate by taking the number that is closest and smaller than the auction's YTM. This is to make the initial price of the bond as close to par value as possible since it would be par value if the coupon rate was exactly equal to the YTM. The reason why they don't simply make it equal is because they want to keep coupon rates a multiple of $\frac{1}{8}=0.125$ percent.
