import pandas as pd
from datetime import datetime

house = pd.read_csv("./loren_data/house_2022-07-15.csv")

#dropping 'owner' because there are too many nulls and '--'
house.drop(columns = ['owner'], inplace = True)

#disclosure_date to datetime
house['disclosure_date'] = pd.to_datetime(house['disclosure_date'], yearfirst=True)

#correcting errors in transcription of transaction_date years
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

#turning 'transaction_date' to datetime
house['transaction_date'] = pd.to_datetime(house['transaction_date'])

#correcting irregular 'amount' entries
house = house.replace(to_replace={'amount':['$1,001 -', '$1,000 - $15,000']}, value= '$1,001 - $15,000')
house = house.replace(to_replace={'amount':['$1,000,000 +', '$1,000,000 - $5,000,000']}, value= '$1,000,001 - $5,000,000')
house = house.replace(to_replace={'amount':['$15,000 - $50,000']}, value= '$15,001 - $50,000')

#converting amount to the high end of range, except for the one '$50,000,000 +' entry, 
#which is converted to 50,000,000. Also makes the values integers.
house['amount'] = house['amount'].str.split(' ') 
for i in range(0, len(house)):
    if len(house.loc[i, 'amount']) == 3:
        house.loc[i, 'amount'] = house.loc[i, 'amount'][2]
    else:
        house.loc[i, 'amount'] = house.loc[i, 'amount'][0]
house['amount'] = house['amount'].map(lambda x: x.replace('$', '').replace(',', ''))
house['amount'] = house['amount'].astype(int)

#reading in company name/ticker symbol table and converting it to dataframe
tickers = pd.read_excel('./loren_data/US-Stock-Symbols.xlsx')
tickers = tickers[['Symbol', 'Name']]
tickers.columns = tickers.columns.map(lambda x: x.lower())

#finding and filling in the missing ticker symbols
for i in house.loc[house['ticker'] == '--']['asset_description']:
    symbol = tickers.loc[tickers['name'] == i, 'symbol']
    house.loc[house['asset_description'] == i, 'ticker'] = symbol
    
#editing columns/column names in preparation for concatenation with the Senate data
house['chamber'] = 'house'
house.drop(columns = ['ptr_link', 'cap_gains_over_200_usd', 'disclosure_year'], inplace = True)
house.rename(columns = {'representative': 'name', 'district': 'represents'}, inplace = True)

#importing current legislators dataframe
current_legislators = pd.read_csv('./loren_data/legislators-current.csv')

#importing historical legislators dataframe
historical_legislators = pd.read_csv('./loren_data/legislators-historical.csv')

#building the dataframe to pull party, gender, and birthday from
historical_legislators['birthday'] = pd.to_datetime(historical_legislators['birthday'], format = '%Y-%m-%d')
current_legislators['birthday'] = pd.to_datetime(current_legislators['birthday'], format = '%Y-%m-%d')
historical_legislators = historical_legislators[historical_legislators['birthday'] > datetime(1922,1, 1)]

relevant_legislators = pd.concat([current_legislators, historical_legislators])
relevant_legislators = relevant_legislators[['last_name', 'first_name', 'middle_name', 'suffix',
                                             'full_name', 'birthday', 'gender', 'type', 'state', 'party',
                                             'district']]

#creating first and last name columns to be able to cross search the dataframes
house['name'] = house['name'].map(lambda x: x.replace("Hon. ", ""))
house['first_name'] = house['name'].map(lambda x: x.split()[0])
house['last_name'] = house['name'].map(lambda x: x.split()[-1])

#cleaning both dataframes
house.loc[house['last_name'] == 'FACS', 'last_name'] = 'Dunn'
house.loc[house['last_name'] == 'Arenholz', 'last_name'] = 'Hinson'

relevant_legislators.loc[relevant_legislators['last_name'].str.contains('Halleran'), 'last_name'] = "O'Halleran"
relevant_legislators.loc[relevant_legislators['last_name'] == 'Sánchez', 'last_name'] = 'Sanchez'

#importing necessary data from relevant_legislators to house
#if this throws an error remove returns from after &s
house['party'] = ''
house['birthday'] = ''
house['gender'] = ''

name = set()
for i in house.index:
    #try:
    first_name = house.loc[i, 'first_name']
    last_name = house.loc[i, 'last_name']
    party = relevant_legislators[(relevant_legislators['first_name'] == first_name) &
                                 (relevant_legislators['last_name'].map(lambda x: x.split()[-1]) == last_name)]['party'].values
    birthday = relevant_legislators[(relevant_legislators['first_name'] == first_name) & 
                                    (relevant_legislators['last_name'].map(lambda x: x.split()[-1]) == last_name)]['birthday'].values
    gender = relevant_legislators[(relevant_legislators['first_name'] == first_name) & 
                                  (relevant_legislators['last_name'].map(lambda x: x.split()[-1]) == last_name)]['gender'].values
    if len(party) == 0:
        party = relevant_legislators[(relevant_legislators['district'] == float(house.loc[i, 'represents'][-2:])) & 
                                     (relevant_legislators['last_name'].map(lambda x: x.split()[-1]) == last_name)]['party'].values
        birthday = relevant_legislators[(relevant_legislators['district'] == float(house.loc[i, 'represents'][-2:])) & 
                                        (relevant_legislators['last_name'].map(lambda x: x.split()[-1]) == last_name)]['birthday'].values
        gender = relevant_legislators[(relevant_legislators['district'] == float(house.loc[i, 'represents'][-2:])) & 
                                      (relevant_legislators['last_name'].map(lambda x: x.split()[-1]) == last_name)]['gender'].values
    if len(party) == 0:
        name.add(str(first_name) + ' ' + str(last_name))
    house.loc[i, 'party'] = party[0]
    house.loc[i, 'birthday'] = birthday[0]
    house.loc[i, 'gender'] = gender[0]
    
#putting birthdays into datetime and removing the first_name and last_name columns
house['birthday'] = pd.to_datetime(house['birthday'], format = '%Y-%m-%d')
house.drop(columns = ['first_name', 'last_name'], inplace = True)

#reading out the cleaned dataframe to .csv
house.to_csv('./loren_data/clean_house_2022-07-15.csv')