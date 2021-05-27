#!/usr/bin/env python
# coding: utf-8

# # Raport covidowy dla Allegro SUMMER E-XPERIENCE
# ## Rekrutacja: Intern - Business Application Administrator

# Table of Contents
# 
# * Przygotowanie danych
#     * Lista wszystkich państw
#     * Lista państw z danymi
#     * Lista państw bez danych
#     * Tabela danych dla wskazanych państw
# * TOP 10 państw z największą liczbą wyzdrowień ...
# * TOP 10 państw z największą liczbą potwierdzonych nowych przypadków ...
# * TOP 10 państw z największą liczbą przypadków śmiertelnych ...
# * Statystyki ... dla Polski za ostatni miesiąc
# * Miesięczny przyrost wyzdrowień w ostatnim miesiącu


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import json
import datetime
import time

pd.set_option('mode.chained_assignment', None)

# # Przygotowanie danych

# ## Lista wszystkich państw

# Źródło: https://api.covid19api.com/countries

# In[710]:


base = "https://api.covid19api.com"

# list of countries
response = requests.get(base + "/countries")
countries_json = response.json()
countries_list = []

for item in countries_json:
    my_list = []
    my_list = item.get('Slug')
    countries_list.append(my_list)

print("Liczba wszystkich państw:", len(countries_list))
print(*countries_list, sep=", ")

# all countries data (without USA)
countries_with_empty_response = []
countries_with_response = []
countries_data_list = []

for country in countries_list:
    response = requests.get(base + '/country/' + country + '?from=2020-04-01T00:00:00Z&to=2021-03-31T00:00:00Z')
    country_response = response.json()

    if len(country_response) <= 2:
        countries_with_empty_response.append(country)
        # print(f'---{country}---{country_response}---')
        continue
    else:
        countries_with_response.append(country)
        # print(f'---{country}---passed---')

        for item in country_response:
            my_dict = {}
            my_dict['Country'] = item.get('Country')
            my_dict['Confirmed'] = item.get('Confirmed')
            my_dict['Deaths'] = item.get('Deaths')
            my_dict['Recovered'] = item.get('Recovered')
            my_dict['Active'] = item.get('Active')
            my_dict['Date'] = item.get('Date')

            countries_data_list.append(my_dict)
    time.sleep(1)

# new df based on list
countries_data_json = json.dumps(countries_data_list)
countries_df = pd.read_json(countries_data_json)

# saving dataframe to csv for safety purpose
countries_df.to_csv('countries_df.csv', index=False)

# countries_df = pd.read_csv("country_df_1.csv")


# period of one year - from
start_date = datetime.date(2020, 4, 1)
end_date = datetime.date(2021, 3, 30)
delta = datetime.timedelta(days=1)

from_dates_list = []

while start_date <= end_date:
    # print(start_date)
    from_dates_list.append(start_date)
    start_date += delta

# print(*from_dates_list, '\n')


# period of one year - to
start_date = datetime.date(2020, 4, 2)
end_date = datetime.date(2021, 3, 31)
delta = datetime.timedelta(days=1)

to_dates_list = []

while start_date <= end_date:
    # print(start_date)
    to_dates_list.append(start_date)
    start_date += delta

# print(*to_dates_list)


usa_data_list = []

for from_date, to_date in zip(from_dates_list, to_dates_list):
    response = requests.get(base + '/country/united-states' + f'?from={from_date}T00:00:00Z&to={to_date}T00:00:00Z')
    usa_data_json = response.json()

    for item in usa_data_json:
        my_dict = {}
        my_dict['Country'] = item.get('Country')
        my_dict['Confirmed'] = item.get('Confirmed')
        my_dict['Deaths'] = item.get('Deaths')
        my_dict['Recovered'] = item.get('Recovered')
        my_dict['Active'] = item.get('Active')
        my_dict['Date'] = item.get('Date')

        usa_data_list.append(my_dict)
    time.sleep(1)

# new df based on list
usa_data = json.dumps(usa_data_list)
country_usa_df = pd.read_json(usa_data)

# saving dataframe to csv for safety purpose
country_usa_df.to_csv('country_usa_df.csv', index=False)

# country_usa_df = pd.read_csv("usa_df_1.csv")


# appending two dfs = world data (190 countries)
countries_and_usa_df = countries_df.append(country_usa_df)

# saving dataframe to csv for safety purpose
countries_and_usa_df.to_csv('countries_and_usa_df.csv', index=False)

# ## Lista państw z danymi


countries_with_response.append('united-states')
print("Liczba państw z danymi", len(countries_with_response))
print(*countries_with_response, sep=", ")

# ## Lista państw bez danych

# Brak danych dla tych państw.


countries_with_response.remove('united-states')
print("Liczba państw bez danych:", len(countries_with_empty_response))
print(*countries_with_empty_response, sep=", ")

# ## Tabela danych dla wkazanych państw

# Źródło: https://api.covid19api.com/country/{{country}}?from=2021-03-01T00:00:00Z&to=2021-03-31T00:00:00Z


countries_and_usa_df

# # TOP 10 państw z największą liczbą wyzdrowień w ostatnim miesiącu


# picking columns from countries_and_usa_df
top_recovered_df = countries_and_usa_df[['Country', 'Recovered', 'Date']]

# data string slicing - reducting data to year-month-day
top_recovered_df['Date'] = top_recovered_df['Date'].astype(str).str[:10]
# back to datatime type
top_recovered_df['Date'] = pd.to_datetime(top_recovered_df['Date'])
# masking date data
date_mask = (top_recovered_df['Date'] >= '2021-3-1') & (top_recovered_df['Date'] <= '2021-3-31')
# re-assign to variable
top_recovered_df = top_recovered_df.loc[date_mask]
top_recovered_df.reset_index(drop=True, inplace=True)

top_recovered_df = top_recovered_df[['Country', 'Date', 'Recovered']].groupby(['Country', 'Date']).sum()
top_recovered_df.reset_index(inplace=True)

# Recovered column copy
top_recovered_df['Test'] = top_recovered_df['Recovered']
# increment empty column
top_recovered_df['Recovered_increment'] = 0

month_limit = 30
df_limit = 5889
index_counter = 0

while month_limit <= df_limit:

    while index_counter <= month_limit and index_counter <= df_limit:
        if index_counter == 5889:
            break
        else:
            top_recovered_df['Recovered_increment'][index_counter + 1] = top_recovered_df['Recovered'][
                                                                             index_counter + 1] - \
                                                                         top_recovered_df['Test'][index_counter]
            index_counter += 1
            # print(index_counter)

    if index_counter >= month_limit:
        month_limit += 31

    # cleaner look to df
top_recovered_df = top_recovered_df[['Country', 'Recovered_increment', 'Date']]
# group by date(month) and sum increment
top_recovered_df = top_recovered_df.groupby(by="Country").sum()

# sorting by increment and return first 10
top_recovered_df = top_recovered_df.sort_values(by='Recovered_increment', ascending=False).head(10)

top_recovered_df

plt.figure(figsize=(10, 7))
sns.barplot(x=top_recovered_df.index, y='Recovered_increment', data=top_recovered_df)
# plt.yticks(range(0, int(14e6), int(2e6)))
plt.xticks(rotation=45)
plt.title("TOP 10 państw z największą liczbą wyzdrowień w ostatnim miesiącu")
plt.grid()
plt.tight_layout();

# # TOP 10 państw z największą liczbą potwierdzonych nowych przypadków zachorowań w ostatnim miesiącu


# picking columns from countries_and_usa_df
top_confirmed_df = countries_and_usa_df[['Country', 'Confirmed', 'Date']]

# data string slicing - reducting data to year-month-day
top_confirmed_df['Date'] = top_confirmed_df['Date'].astype(str).str[:10]
# back to datatime type
top_confirmed_df['Date'] = pd.to_datetime(top_confirmed_df['Date'])
# masking date data
date_mask = (top_confirmed_df['Date'] >= '2021-3-1') & (top_confirmed_df['Date'] <= '2021-3-31')
# re-assign to variable
top_confirmed_df = top_confirmed_df.loc[date_mask]
top_confirmed_df.reset_index(drop=True, inplace=True)

top_confirmed_df = top_confirmed_df[['Country', 'Date', 'Confirmed']].groupby(['Country', 'Date']).sum()
top_confirmed_df.reset_index(inplace=True)

# Recovered column copy
top_confirmed_df['Test'] = top_confirmed_df['Confirmed']
# increment empty column
top_confirmed_df['Confirmed_increment'] = 0

month_limit = 30
df_limit = 5889
index_counter = 0

while month_limit <= df_limit:

    while index_counter <= month_limit and index_counter <= df_limit:
        if index_counter == 5889:
            break
        else:
            top_confirmed_df['Confirmed_increment'][index_counter + 1] = top_confirmed_df['Confirmed'][
                                                                             index_counter + 1] - \
                                                                         top_confirmed_df['Test'][index_counter]
            index_counter += 1
            # print(index_counter)

    if index_counter >= month_limit:
        month_limit += 31

    # cleaner look to df
top_confirmed_df = top_confirmed_df[['Country', 'Confirmed_increment', 'Date']]
# group by date(month) and sum increment
top_confirmed_df = top_confirmed_df.groupby(by="Country").sum()

# sorting by increment and return first 10
top_confirmed_df = top_confirmed_df.sort_values(by='Confirmed_increment', ascending=False).head(10)

top_confirmed_df

plt.figure(figsize=(10, 7))
sns.barplot(x=top_confirmed_df.index, y='Confirmed_increment', data=top_confirmed_df)
# plt.yticks(range(0, int(14e6), int(2e6)))
plt.xticks(rotation=45)
plt.title("TOP 10 państw z największą liczbą potwierdzonych nowych przypadków zachorowań w ostatnim miesiącu")
plt.grid()
plt.tight_layout();

# # TOP 10 państw z największą liczbą przypadków śmiertelnychw ostatnim miesiącu


# picking columns from countries_and_usa_df
top_deaths_df = countries_and_usa_df[['Country', 'Deaths', 'Date']]

# data string slicing - reducting data to year-month-day
top_deaths_df['Date'] = top_deaths_df['Date'].astype(str).str[:10]
# back to datatime type
top_deaths_df['Date'] = pd.to_datetime(top_deaths_df['Date'])
# masking date data
date_mask = (top_deaths_df['Date'] >= '2021-3-1') & (top_deaths_df['Date'] <= '2021-3-31')
# re-assign to variable
top_deaths_df = top_deaths_df.loc[date_mask]
top_deaths_df.reset_index(drop=True, inplace=True)

top_deaths_df = top_deaths_df[['Country', 'Date', 'Deaths']].groupby(['Country', 'Date']).sum()
top_deaths_df.reset_index(inplace=True)

# Recovered column copy
top_deaths_df['Test'] = top_deaths_df['Deaths']
# increment empty column
top_deaths_df['Deaths_increment'] = 0

month_limit = 30
df_limit = 5889
index_counter = 0

while month_limit <= df_limit:

    while index_counter <= month_limit and index_counter <= df_limit:
        if index_counter == 5889:
            break
        else:
            top_deaths_df['Deaths_increment'][index_counter + 1] = top_deaths_df['Deaths'][index_counter + 1] - \
                                                                   top_deaths_df['Test'][index_counter]
            index_counter += 1
            # print(index_counter)

    if index_counter >= month_limit:
        month_limit += 31

    # cleaner look to df
top_deaths_df = top_deaths_df[['Country', 'Deaths_increment', 'Date']]
# group by date(month) and sum increment
top_deaths_df = top_deaths_df.groupby(by="Country").sum()

# sorting by increment and return first 10
top_deaths_df = top_deaths_df.sort_values(by='Deaths_increment', ascending=False).head(10)

top_deaths_df

plt.figure(figsize=(10, 7))
sns.barplot(x=top_deaths_df.index, y='Deaths_increment', data=top_deaths_df)
# plt.yticks(range(0, int(14e6), int(2e6)))
plt.xticks(rotation=45)
plt.title("# TOP 10 państw z największą liczbą przypadków śmiertelnychw ostatnim miesiącu")
plt.grid()
plt.tight_layout();

# # Statystyki z wyzdrowień, nowych przypadków zachorowań oraz przypadków śmiertelnych dla Polski za ostatni miesiąc


# reduce countries_df to Poland records
poland_df = countries_df.loc[countries_df["Country"] == 'Poland']
poland_df.reset_index(drop=True, inplace=True)

# data string slicing - reducting data to year-month-day
poland_df['Date'] = poland_df['Date'].astype(str).str[:10]
# back to datatime type
poland_df['Date'] = pd.to_datetime(poland_df['Date'])
# masking date data
date_mask = (poland_df['Date'] >= '2021-3-1') & (poland_df['Date'] <= '2021-3-31')
# re-assign to variable
poland_df = poland_df.loc[date_mask]
poland_df.reset_index(drop=True, inplace=True)

# managing outliner
idx = poland_df.index[poland_df['Active'] > 1e6].tolist()
poland_df.iloc[idx[0], 4] = poland_df.iloc[idx[0], 1] - poland_df.iloc[idx[0], 2] - poland_df.iloc[idx[0], 3]

poland_df

fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)

plt.suptitle("Statystyki dla Polski za ostatni miesiąc", fontsize=14)

sns.lineplot(ax=axes[0], data=poland_df, x='Date', y='Confirmed', color='orange', linewidth=2)
axes[0].set_title("Confirmed")
axes[0].set_yticks(range(int(16e5), int(25e5), int(1e5)))
axes[0].grid(True)

sns.lineplot(ax=axes[1], data=poland_df, x='Date', y='Deaths', color='red', linewidth=2)
axes[1].set_title("Deaths")
axes[1].set_yticks(range(42000, 56000, 2000))
axes[1].grid(True)

sns.lineplot(ax=axes[2], data=poland_df, x='Date', y='Recovered', color='green', linewidth=2)
axes[2].set_title("Recovered")
axes[2].set_yticks(range(int(14e5), int(20e5), int(1e5)))
axes[2].grid(True)

sns.lineplot(ax=axes[3], data=poland_df, x='Date', y='Active', color='blue', linewidth=2)
axes[3].tick_params(axis='x', rotation=90)
axes[3].set_title("Active")
axes[3].set_yticks(range(200000, 480000, 40000))
axes[3].set_xticks(poland_df['Date'])
axes[3].grid(True)

# plt.tight_layout();


# # Miesięczny przyrost wyzdrowień w ostatnim roku


# picking columns from countries_and_usa_df
top_recovered_df = countries_and_usa_df[['Country', 'Recovered', 'Date']]

# data string slicing - reducting data to year-month-day
top_recovered_df['Date'] = top_recovered_df['Date'].astype(str).str[:7]

top_recovered_df = top_recovered_df[['Country', 'Date', 'Recovered']].groupby(['Country', 'Date']).sum()
top_recovered_df.reset_index(inplace=True)

# Recovered column copy
top_recovered_df['Test'] = top_recovered_df['Recovered']
# increment empty column
top_recovered_df['Recovered_increment'] = 0

month_limit = 30
df_limit = 2279
index_counter = 0

while month_limit <= df_limit:

    while index_counter <= month_limit and index_counter <= df_limit:
        if index_counter == 2279:
            break
        else:
            top_recovered_df['Recovered_increment'][index_counter + 1] = top_recovered_df['Recovered'][
                                                                             index_counter + 1] - \
                                                                         top_recovered_df['Test'][index_counter]
            index_counter += 1
            # print(index_counter)

    if index_counter >= month_limit:
        month_limit += 31

top_recovered_df.loc[top_recovered_df['Recovered_increment'] < 0, 'Recovered_increment'] = 0

# cleaner look to df
top_recovered_df = top_recovered_df[['Country', 'Recovered', 'Recovered_increment', 'Date']]
# group by date(month) and sum increment
top_recovered_df = top_recovered_df.groupby(by="Date").sum()

# sorting by increment and return first 10
top_recovered_df = top_recovered_df.sort_values(by='Date', ascending=True)

top_recovered_df

fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

plt.suptitle("Miesięczny przyrost wyzdrowień w ostatnim roku", fontsize=14)

sns.lineplot(ax=axes[0], data=top_recovered_df, x='Date', y='Recovered_increment', color='red', linewidth=2)
axes[0].set_title("Increment")
# axes[0].set_yticks(range(0, 600000, 100000))
axes[0].grid(True)

sns.lineplot(ax=axes[1], data=top_recovered_df, x='Date', y='Recovered', color='green', linewidth=2)
axes[1].set_title("Recovered")
axes[1].tick_params(axis='x', rotation=45)
axes[1].grid(True)

plt.tight_layout();
