import pandas as pd
from datetime import datetime
import re

 #one team member needs this on their computer so we included it, just in case
proxies = {'https': 'http://127.0.0.1:7769'}

house = pd.read_csv("./data/house_2022-07-15.csv")

#dropping 'owner'
house.drop(columns = ['owner'], inplace = True)

#this drops the 4 rows with null asset descriptions
house.dropna(inplace = True)

#changing disclosure date and transaction date to datetimes
#there were some apparent transcription errors in transaction date
#that's corrected before the transaction date conversion
house['disclosure_date'] = pd.to_datetime(house['disclosure_date'], yearfirst=True)

house['transaction_date'] = house['transaction_date'].str.split('-')

weird_years = house[(house['transaction_date'].str[0] != '2017') &
      (house['transaction_date'].str[0] != '2018') &
      (house['transaction_date'].str[0] != '2019') &
      (house['transaction_date'].str[0] != '2020') &
      (house['transaction_date'].str[0] != '2021') &
      (house['transaction_date'].str[0] != '2022')]

for i in weird_years.index:
    house.loc[i, 'transaction_date'][0] = str(house.loc[i, 'disclosure_year'])

house['transaction_date'] = house['transaction_date'].str.join('-')
house['transaction_date'] = pd.to_datetime(house['transaction_date'])
house.dtypes

#cleaning amounts and replacing with highest value
house = house.replace(to_replace={'amount':['$1,001 -', '$1,000 - $15,000']}, value= '$1,001 - $15,000')
house = house.replace(to_replace={'amount':['$1,000,000 +', '$1,000,000 - $5,000,000']}, value= '$1,000,001 - $5,000,000')
house = house.replace(to_replace={'amount':['$15,000 - $50,000']}, value= '$15,001 - $50,000')
house['amount'].value_counts()

house['amount'] = house['amount'].str.split(' ') 

for i in house.index:
    if len(house.loc[i, 'amount']) == 3:
        house.loc[i, 'amount'] = house.loc[i, 'amount'][2]
    else:
        house.loc[i, 'amount'] = house.loc[i, 'amount'][0]
        
house['amount'] = house['amount'].map(lambda x: x.replace('$', '').replace(',', ''))
house['amount'] = house['amount'].astype(int)
house['amount'].value_counts()

#tickers. start by filling as many '--' in as we can.
tickers = pd.read_excel('./data/US-Stock-Symbols.xlsx')
tickers = tickers[['Symbol', 'Name']]
tickers.columns = tickers.columns.map(lambda x: x.lower())

#these unhelpful elements appeared in senate data so we included them for 
#the house, for good measure, though they don't appear to have helped with the house
#data
house['asset_description'] = house['asset_description'].str.replace(' &amp;', '')
house['asset_description'] = house['asset_description'].str.replace(' Common Stock', '')
house['asset_description'] = house['asset_description'].str.replace(' CMN', '')
house['asset_description'] = house['asset_description'].str.replace(' ETF', '')

#this adds names to the ticker dataframe so we can fill in more '--'
#again, it includes elements from both the house (df2) and the senate (df3)
df2 = pd.DataFrame({
    'symbol': ['FLX', 'TDDXX', 'NFG', 'PM', 'LIN', 'GPN', 'EQIX', 'PYPL', 'TDDXX', 'FSEN', 'TDDXX', 'ZBH', 'ORCL', 'UNH', 'EXPE',
              'ADYEY', 'WFC'],
    'name': ['Netflix Inc', 'BLF FedFund TDDXX', 'National Fuel Gas Company', 'Philip Morris International Inc', 
             'Linde plc Ordinary Share', 'Global Payments Inc', 'Equinix Inc', 'Paypal Holdings Inc', 'BLF FedFund TDD XX', 
             'FS Energy & Power Fund Common', 'BLF FedFun TDDXX', 'Zimmer Biomet Holdings', 'Oracle Corp', 'United Health',
             'Expedia Group Inc', 'ADYEN N V ADR', 'West Fargo N D']
})

df3 = pd.DataFrame({
    'symbol': ['CAB', 'PFE', 'AAPL', 'AMZN', 'NKE', 'PCP', 'UAA', 'LIT', 'NFLX', 'FEZ', 'CIT', 'LNT', 'WW', 'UAA', 'PHLD'],
    'name': ["Cabela's Inc", 'Pfizer Inc', 'aapl', 'Amazon', 'Nike Inc B', 'Precision Castparts Corp', 
             'Under Armour Inc', 'Global X Lithium Battery', 'nflx', 'SPDR Euro Stoxx 50', 'CIT Group Inc (CIT)',
            'Alliant Energy Corp', 'Weight Watchers Intl Inc', 'Under Armour Inc Cl A', 'PHLD - Phillips Edison Grocery Center REIT I']
})

tickers = pd.concat([tickers, df2, df3])

for i in house.loc[house['ticker'] == '--']['asset_description']:
    symbol = tickers.loc[tickers['name'] == i, 'symbol'].values
    if len(symbol) != 0:
        house.loc[house['asset_description'] == i, 'ticker'] = symbol[0]

#dropping the rows with remaining '--'
house = house[house['ticker'] != '--']

#type. getting them down to just purchase, sale, and partial sale
house = house[house['type'] != 'exchange']
#fixing one type entered as 'sale'. opted to call it 'sale_full'
house.loc[house['type'] == 'sale', 'type'] = 'sale_full'

house['chamber'] = 'house'
house.drop(columns = ['ptr_link', 'cap_gains_over_200_usd', 'disclosure_year'], inplace = True)
house.rename(columns = {'representative': 'name', 'district': 'represents'}, inplace = True)

#filling in party, birthday, and gender data
current_legislators = pd.read_csv('./data/legislators-current.csv')
historical_legislators = pd.read_csv('./data/legislators-historical.csv')

historical_legislators['birthday'] = pd.to_datetime(historical_legislators['birthday'], format = '%Y-%m-%d')
current_legislators['birthday'] = pd.to_datetime(current_legislators['birthday'], format = '%Y-%m-%d')
historical_legislators = historical_legislators[historical_legislators['birthday'] > datetime(1922,1, 1)]

legislators = pd.concat([current_legislators, historical_legislators])
legislators = legislators[['last_name', 'first_name', 'middle_name', 'suffix',
                                             'full_name', 'birthday', 'gender', 'type', 'state', 'party', 'district']]

#cleaning in prep for inputing additional data
house['name'] = house['name'].map(lambda x: x.replace("Hon. ", ""))
house['first_name'] = house['name'].map(lambda x: x.split()[0])
house['last_name'] = house['name'].map(lambda x: x.split()[-1])

house.loc[house['last_name'] == 'FACS', 'last_name'] = 'Dunn'
house.loc[house['last_name'] == 'Arenholz', 'last_name'] = 'Hinson'

legislators.loc[legislators['last_name'].str.contains('Halleran'), 'last_name'] = "O'Halleran"
legislators.loc[legislators['last_name'] == 'Sánchez', 'last_name'] = 'Sanchez'

house['party'] = ''
house['birthday'] = ''
house['gender'] = ''

name = set()
for i in house.index:
    #try:
    first_name = house.loc[i, 'first_name']
    last_name = house.loc[i, 'last_name']
    party = legislators[(legislators['first_name'] == first_name) & (legislators['last_name'].map(lambda x: x.split()[-1]) == last_name)]['party'].values
    birthday = legislators[(legislators['first_name'] == first_name) & (legislators['last_name'].map(lambda x: x.split()[-1]) == last_name)]['birthday'].values
    gender = legislators[(legislators['first_name'] == first_name) & (legislators['last_name'].map(lambda x: x.split()[-1]) == last_name)]['gender'].values
    if len(party) == 0:
        party = legislators[(legislators['district'] == float(house.loc[i, 'represents'][-2:])) & (legislators['last_name'].map(lambda x: x.split()[-1]) == last_name)]['party'].values
        birthday = legislators[(legislators['district'] == float(house.loc[i, 'represents'][-2:])) & (legislators['last_name'].map(lambda x: x.split()[-1]) == last_name)]['birthday'].values
        gender = legislators[(legislators['district'] == float(house.loc[i, 'represents'][-2:])) & (legislators['last_name'].map(lambda x: x.split()[-1]) == last_name)]['gender'].values
    if len(party) == 0:
        name.add(str(first_name) + ' ' + str(last_name))
    house.loc[i, 'party'] = party[0]
    house.loc[i, 'birthday'] = birthday[0]
    house.loc[i, 'gender'] = gender[0]

#birthdays to datetime and dropping unnecessary columns
house['birthday'] = pd.to_datetime(house['birthday'], format = '%Y-%m-%d')

###
#senate data cleaning starts here.
###
senate = pd.read_csv('data/all_transactions_senate.csv')

#converting to datetimes
senate['transaction_date'] = pd.to_datetime(senate['transaction_date'])
senate['disclosure_date'] = pd.to_datetime(senate['disclosure_date'])
senate['transaction_date'] = pd.to_datetime(senate['transaction_date'], format = '%Y-%m-%d')
senate['disclosure_date'] = pd.to_datetime(senate['disclosure_date'], format = '%Y-%m-%d')

#dropping owner
senate.drop(columns = ['owner'], inplace = True)

#dropping asset types we don't want
#given that we're trying to keep NaNs at this point,
#more efficient methods weren't working, so we used this less scalable approach,
#which gets the job done
senate = senate[senate['asset_type'] != 'Municipal Security']
senate = senate[senate['asset_type'] != 'Corporate Bond']
senate = senate[senate['asset_type'] != 'Non-Public Stock']
senate = senate[senate['asset_type'] != 'Commodities/Futures Contract']
senate = senate[senate['asset_type'] != 'Cryptocurrency']
senate = senate[senate['asset_type'] != 'PDF Disclosed Filing']

#dropping type == Echange
senate = senate[senate['type'] != 'Exchange']

#making sale, etc., match House in format
senate['type'] = senate['type'].map({
    'Purchase': 'purchase',
    'Sale (Full)': 'sale_full',
    'Sale (Partial)': 'sale_partial'
                                    })

#cleaning asset_description in prep for mapping to ticker symbols
senate['asset_description'] = senate['asset_description'].str.replace(' &amp;', '')
senate['asset_description'] = senate['asset_description'].str.replace(' Common Stock', '')
senate['asset_description'] = senate['asset_description'].str.replace(' CMN', '')
senate['asset_description'] = senate['asset_description'].str.replace(' ETF', '')

#mapping to ticker symbols
symbol_set = set()
for i in senate.loc[senate['ticker'] == '--']['asset_description']:
    if i in tickers['name'].unique():
        symbol = tickers.loc[tickers['name'] == i, 'symbol'].values
        symbol_set.add(symbol[0])
        senate.loc[((senate['ticker'] == '--') & (senate['asset_description'] == i)), 'ticker'] = symbol[0]

senate['possible_ticker'] = ''

for i in senate[senate['ticker'] == '--']['asset_description'].index:
    asset_descr = senate.loc[i, 'asset_description']
    ticker = re.findall('[A-Z]{2,6}', asset_descr)
    if len(ticker) == 1 and ticker != 'LLC' and ticker != 'ETF':
        senate.loc[i, 'possible_ticker'] = ticker[0]

for i in senate.loc[senate['ticker'] == '--']['possible_ticker']:
    if i in tickers['symbol'].unique():
        symbol = tickers.loc[tickers['symbol'] == i, 'symbol'].values
        senate.loc[((senate['ticker'] == '--') & (senate['possible_ticker'] == i)), 'ticker'] = symbol[0]

#dropping the columns used for this process
senate.drop(columns = 'possible_ticker', inplace = True)

#dropping the remaining '--'
senate = senate[senate['ticker'] != '--']

#eliminating unnecessary columns
senate = senate.drop(columns=['asset_type', 'comment', 'ptr_link'])

#converting amounts to highest value
senate['amount'] = senate['amount'].str.split(' ') 

for i in senate.index:
    if len(senate.loc[i, 'amount']) == 3:
        senate.loc[i, 'amount'] = senate.loc[i, 'amount'][2]
    else:
        senate.loc[i, 'amount'] = senate.loc[i, 'amount'][1]
        
senate['amount'] = senate['amount'].map(lambda x: x.replace('$', '').replace(',', ''))
senate['amount'] = senate['amount'].astype(int)

#column names and chamber = senate to match house columns
senate.rename(columns = {'senator':'name'}, inplace = True)
senate['chamber'] = 'senate'

#getting info on party, birthday, gender, and 'represents' (state)

#getting some names into desired format/cleaning
senate['name'] = senate['name'].map(lambda x: x.replace(', Jr.', ''))
senate['name'] = senate['name'].map(lambda x: x.replace(', Jr', ''))
senate['name'] = senate['name'].map(lambda x: x.replace(', Iv', ''))
senate['name'] = senate['name'].map(lambda x: x.replace(', Iii', ''))
senate['name'] = senate['name'].map(lambda x: x.replace('Jerry Moran,', 'Jerry Moran'))

#creating first and last name columns and cleaning
senate['first_name'] = senate['name'].map(lambda x: x.split()[0])
senate['last_name'] = senate['name'].map(lambda x: x.split()[-1])
senate.loc[senate['first_name']== 'A.', 'first_name'] = 'Mitchell'
senate.loc[senate['last_name']== 'Mcconnell', 'last_name'] = 'McConnell'
senate.loc[senate['last_name']== 'Hollen', 'last_name'] = 'Van Hollen'

#adding into
senate['party'] = ''
senate['birthday'] = ''
senate['gender'] = ''
senate['represents'] = ''

name = set()
for i in senate.index:

    last_name = senate.loc[i, 'last_name']
    party = legislators[(legislators['last_name'] == last_name)]['party'].values #(legislators['first_name'] == first_name) & 
    birthday = legislators[(legislators['last_name'] == last_name)]['birthday'].values #(legislators['first_name'] == first_name) & 
    gender = legislators[(legislators['last_name'] == last_name)]['gender'].values #(legislators['first_name'] == first_name) &
    state = legislators[(legislators['last_name'] == last_name)]['state'].values #(legislators['first_name'] == first_name) &
    if len(party) == 0:
        name.add(str(first_name) + ' ' + str(last_name))
    senate.loc[i, 'party'] = party[0]
    senate.loc[i, 'birthday'] = birthday[0]
    senate.loc[i, 'gender'] = gender[0]
    senate.loc[i, 'represents'] = state[0]

#birthday to datetime
senate['birthday'] = pd.to_datetime(senate['birthday'], format = '%Y-%m-%d')

#building new dataframe
all_reps = pd.concat([senate, house], axis = 0)

#converting these back to datetime
all_reps['transaction_date'] = pd.to_datetime(all_reps['transaction_date'], format = '%Y-%m-%d')
all_reps['disclosure_date'] = pd.to_datetime(all_reps['disclosure_date'], format = '%Y-%m-%d')
all_reps['birthday'] = pd.to_datetime(all_reps['birthday'], format = '%Y-%m-%d')

#fixing index
all_reps.reset_index(drop = True, inplace = True)

#outputting final data set, ticker data, and relevant reps data.
all_reps.to_csv('./data/cleaned_complete_congress_data.csv', index = False)
tickers.to_csv('data/ticker_symbols.csv', index = False)
legislators.to_csv('data/relevant_legislators.csv', index = False)