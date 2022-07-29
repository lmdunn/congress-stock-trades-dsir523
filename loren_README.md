# KLM Data for Public Service
## Congressional Equities Trading, 2014-2022
-----
Recent news reports from sources such as [U.S. News & World Report](https://money.usnews.com/investing/articles/congress-and-stocks-notable-trades-and-an-ineffective-law) and [Harvard Political Review](https://harvardpolitics.com/congressional-stock-trading/) have raised questions about whether or not congresspeople are leveraging insider information for financial gain through their personal or familial investments. Past studies of the available data ([Ziobrowski, et al, 2004](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/abs/abnormal-returns-from-the-common-stock-investments-of-the-us-senate/A39406479940758D59E09FDCB8EE9BEC) and [Ziobrowski, et al, 2011](https://www.cambridge.org/core/journals/business-and-politics/article/abnormal-returns-from-the-common-stock-investments-of-members-of-the-us-house-of-representatives/BC6C6A524BBE96738BB94D37EF0FD1A5)) has shown evidence of congresspeople outperforming the average investor by significant amounts, suggesting congresspeople are either especially savvy investors, as a rule, or that they are, in fact, leveraging insider information to their advantage.

With the passage of the STOCK Act of 2012, congresspeople are now required by law to report a wide variety of financial transactions within 45 days, as opposed to the annual declaration required previously. These disclosures, themselves, are not directly available online. Rather, one must visit congressional offices in Washington, D.C. to view the disclosures. Fortunately, there are folks like the people who run [housestockwatcher.com](https://housestockwatcher.com/) and [senatestockwatcher.com](https://senatestockwatcher.com/) who have visted the offices, transcribed the reports, and made the data available online.

We at KLM Data for Public Service have decided to address the question what, if any, evidence there is that congresspeople have engaged in leveraging insider information for financial advantage in the years since the two Ziobrwoski, et al studies.

## The Data
-----

IMPORTANT NOTE: The data we use throughout our analysis is available at [this link](https://drive.google.com/drive/folders/1LG5bKuLBJXHF2HL9jAuEtyCQbmk8m3lS?usp=sharing). To replicate the analysis, please download this data and put it into the "data" folder associated with [our GitHub repository](https://github.com/lmdunn/congress-stock-trades-dsir523).

The data for this analysis came from multiple sources:
1. House of Representatives disclosure information from [housestockwatcher.com](https://housestockwatcher.com/api) on July 15, 2022 at 5:00 PM. (file: `house_2022-07-15.csv`)

2. Senate disclosure information from [senatestockwatcher.com](https://senatestockwatcher.com/api) (file: `all_transactions_senate.csv`)

3. Lists of current and historic US legislators from [this GitHub repository](https://github.com/unitedstates/congress-legislators/), pulled July 19, 2022. (files: `legislators-current.csv`, `legislators-historic.csv`. These were combinedl, with some cleaning, into `relevant-legislators.csv`)

4. [AlphaVantage API](https://www.alphavantage.co/)

5. A list of US stock trading symbols from [tradinggraphs.com](https://www.tradinggraphs.com/2012/05/06/complete-us-stock-symbols-list-nasdaq-nyse-amex/), pulled on July 25, 2022. (file: US-Stock-Symbols.xlsx)

### Data Dictionary
-----
From the data above, we created three data sets we worked from primarily.

#### filled_reps_data.csv and filled_reps_data2.csv

NOTES: 
1. These two data sets are almost identical. The difference is that filled_reps_data.csv includes a daily tracking of the change in value of the position (profit/loss) until the position is closed, while filled_reps_data2.csv includes a daily tracking of the cumulative profit/loss of the position during the entire period of the analysis. In other words, the second data set carries any profit or loss forward from the day of the sale to 2022-07-15, which aids in tracking the overall success of the portfolio over time.
2. The indices were preserved from the initial cleaned file (cleaned_complete_congress_data.csv) in order to make it possible to reference back to that, if necessary.

|Feature|Type|Description|
|---|---|---|
|transaction_date|object|The transaction date listed on the disclosure.|
|ticker|object|The ticker symbol for the stock traded on this transaction.|
|asset_description|object|The name of the company traded.|
|type|object|Purchase or full sale. (Note: we eliminated partial sales on this analysis, though we'd like to include them ina future analysis)|
|amount|int|The estimated amount (in $US) of the transaction. Disclosures present a range. We chose to use the high end of the range for the amount.|
|name|object|The full name of the legislator.|
|disclosure_date|object|The date of the disclosure.|
|chamber|object|Whether the legislator is a Senator or Representative.|
|first_name|object|Legislator's first name.|
|last_name|object|Legislator's last name.|
|party|object|Legislator's political party.|
|birthday|datetime|Legislator's birthday.|
|gender|object|Legislator's gender.|
|represents|object|State or district legislator represents.|
|shares|float|Estimated number of shares purchased, based on amount and adjusted closing prices.|
|start_value|float|Estimated starting value (in $US) of position. Based either directly on amount for purchases or calculated from estimated shares and starting_price for sales.|
|end_value|float|Estimated ending value (in $US) of position. Based either directly on amount for sales or calculated from estimated shares and ending_price for purchases.|
|start_date|object|Estimated start date of position. Either a)the transaction date, b) the first trading day after the transaction date, or c) the first date in the period of our analysis on which the stock traded.|
|end_date|object|Estimated end date of position. Either a)the transaction date, b) the first trading day after the transaction date, or c) the last date in the period of our analysis on which the stock traded.|
|start_price|float|Stock price (in $US) on the start_date.|
|end_price|float|Stock price (in $US) on the end_date.|
|purchase-sale|int|This indicates if a purchase in one transaction was matched with a sale in another. 1 indicates yes/true, 0 indication no/false.|
|DATE COLUMNS|float or int|These columns cover the dates from 2014-01-02 through 2022-07-15. They show either the cumulative profit or loss for every day a position was held (data) or for every day in the period of analysis (data2). Because of the way the dataframe was built, integer 0s were replaced by floats for days there was a change in value, but on the days there was no change in value, integer 0s remain. Thus, on some dates where there were no changes at all, the column remained an integer. That's fixed in the code so future outputs should all be floats for these rows, but given the time necessary to otuput these data sets, we won't be able to change them before our deadline.|

#### complete_daily.csv
This data set tracks the values of the entire congressional portfolio based on the positions held on each day. In other words, each day reflects the net profit of all positions currently held (since those positions were first taken). This data set can be used to look at the volume (measured in dollars) of congressional investment over time.

|Feature|Type|Description|
|---|---|---|
|index|datetime|The index represents every date from 2014-01-02 to 2022-07-15.|
|portfolio_basis|float|The basis value (in $US) of that day's current holdings in the stock market. In other words, the sum of the initial value of all the positions still held on that day.|
|portfolio_delta|float|The cumulative change in value (in $US) of all the positions held on that day **from the first day each position was taken**.|
|percent_change|float|The cumulative percent change in value of all the positions held on that day **from the first day each position was taken**.|


#### complete_daily2_cumulative.csv
This data set tracks the cumulative profit and loss of the entire congressional portfolio over the period of our analysis. It can be used to compare congressional performance to other metrics (e.g. the performance of the S&P 500).

|Feature|Type|Description|
|---|---|---|
|index|datetime|The index represents every date from 2014-01-02 to 2022-07-15.|
|portfolio_basis|float|The basis value (in $US) of all positions taken to that date, including those that have since been sold. With the portfolio delta, this gives a basis for measuring cumulative profit and loss over time.|
|portfolio_delta|float|The net profit/loss (in $US) of all transactions **from the first day each position was taken**, including those positions already sold. With the portfolio basis, this gives a basis for measuring cumulative profit and loss over time.|
|percent_change|float|The cumulative percent change in value of all trading **from the first day each position was taken**.|

## Brief Summary of the Analysis
-----
### Summary of Cleaning
The most important decisions we made during cleaning, both in initial cleaning and feature engineering:
1. We chose to use the high end of the range of value of the transactions (which we ultimately labeled `'amount'` of transaction). In the face of an otherwise arbitrary decision, we thought it would be rational for legislators to try to come in just under a limit, rather than just over.
2. We use adjusted stock prices, which happened to be closing prices, for our stock prices, in order to take splits and other idiosyncracies into account.
3. We opted to drop partial sales because we didn't have time to develop the more complex code necessary to account for those. 
4. We dropped any transaction that wasn't a stock transaction or didn't have a ticker we could identify in the Alpha Vantage records.
### Summary of Feature Engineering
After initial cleaning, we joined our data set of legislator transactions with data we pulled from Alpha Vantage API, filling in pricing data that also enabled us to estimate the size of stock positions. From there, we were able to calculate profit and loss on a daily basis over the period of the analysis. We then built an additional dataframe tracking the basis for each position (the initial value of that position). Using data from both dataframes, we built a datetime indexed dataframe with cumulative basis, profit/loss, and percent change.

We did this in two parallel processes, producing one dataframe that's optimal for looking at changes in the size of congressional holdings over time and another that's optimal for looking at cumulative profit/loss over time, for comparison to market indices and other benchmarks, as described above under "The Data".

Additional cleaning happened during this stage, as well.
### Summary of EDA
PLEASE FILL THIS IN MATT
### Summary of Modeling
PLEASE FILL THIS IN KYLE.

## Conclusions and Recommendations
-----
KYLE I THINK YOU MIGHT BE BEST POSITIONED TO FILL THIS IN.