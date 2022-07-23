It looks like we could donate to them. That might also make it easier to reach out to them and get questions answered.

House Stock Watcher links to a copy of the disclosure forms, which is terrific. So we can see individual ones if we need to.

I also found [this site](https://fd.house.gov/reference/asset-type-codes.aspx) that contains the reference codes we need to identify what kinds of transactions appear in the disclosures. It looks like stocks are Schedule B transactions. You can read about them in this [House Ethics Guidelines: 2021 Instructional Guide](https://ethics.house.gov/sites/ethics.house.gov/files/documents/FINAL%202021%20FD%20Instructions.pdf) starting on page 27. It appears brokerage accounts and other assets are Schedule A, purchases and sales over $1k, Schedule B. In reading this guide, _purchase_ disclosed on Schedule B will almost always be on Schedule A, too (the asset itself appearing). Sales maybe not.

NOTE: there doesn't appear to be a data dictionary and there are few things I'm not clear on right now.
1. what is the difference between a "sale_full" and a "sale_partial"? Does this mean they know the size of the position and whether or not the whole position is sold? Is it something else? Reading the 2021 Instructional Guide confirms that partial sales are to be marked as such.

Items I looked at in Cleaning with notes:
1. the datatypes will need to be changed. COME BACK TO THIS
2. the null "owner" seems likely to be irrelevant, but that needs a decision. These are apx 38% of the data, so we don't want to drop the rows. I'm going to drop the column. It would be interesting to look at ownership patterns, but regardless of who actually owns, the point is congresspeople can use information through family so the distinction isn't too important. 
    Here's the breakdown of the 'owner' column
    NaN          5614
    joint        4635
    self         2897
    --           1315
    dependent     394
4. Messed up transaction dates: Index 2413 had this for the transaction date: '0009-06-09'. Based on disclosure_year and disclosure_date it seems pretty certain the 0009 should have been 2021. Similar story for 4170 (0021-08-02). Also, 11197, 11198 (these two could be duplicates), 10169. NOTE: In examining these it appears there were 2 2017 transactions that were just disclosed in 2022. There are 2022 from 2018. Most of those and the 2017 ones are from Thomas Suozzi. I created a column of just first four digits to make it easier to find (changed to int because I thought I was going to do greater than less than and could have done that without slicing off 4 digits). Then I found 7984 was '20221-'etc. Based on other columns should have been 2021
5. NOTE: It's possible some disclosure dates are messed up -- CHECK FOR OUTLIERS
6. The ranges of numbers seem inconsistent:
    $1,001 - $15,000            10447
    $15,001 - $50,000            2362
    $50,001 - $100,000            750
    $100,001 - $250,000           572
    $250,001 - $500,000           243
    $1,001 -                      242
    $500,001 - $1,000,000         150
    $1,000,001 - $5,000,000        41
    $1,000,000 +                   30
    $5,000,001 - $25,000,000        9
    $1,000 - $15,000                4
    $15,000 - $50,000               3
    $50,000,000 +                   1
    $1,000,000 - $5,000,000         1
    I believe the "$1,001 "is supposed to be 1001-15000 because they don't need to report <$1000. "$\n1000-1500" should be $1001-15000. "$\n1,000,000 +" to "$\n1,000,000 - $\n5,000,000". $\n1,000,000 - $\n5,000,000. "$15,000 - $50,000" to $15,001 - $50,000".
7. I think we should use the high end of the range. I think there's incentive to come in at that place. I think the decision is a bit arbitrary, though there is reason to think in the upper part of the range versus lower (politics). And if they don't want people assumging the high end of the range, they can change the law and make it specific or more smaller ranges.
8. Found an xlsx sheet with tickers and company names on [this site](https://www.tradinggraphs.com/2012/05/06/complete-us-stock-symbols-list-nasdaq-nyse-amex/). I think there are some errors (Bank of America appears as 'BAC^I'). If we run into trouble calling stock prices, we can fix it.

drop 

fix years, way that scales
turn amount to an integer
clean up notebook
make .py file