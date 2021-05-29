import datetime
import json
import time
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns


def main(debug: Optional[bool] = False):
    pd.options.mode.chained_assignment = None

    if debug:
        global api_data  # debug mode

    # ----------------API handling----------------
    api_decision = input("Do you want to do API requests? (requires ~20 minutes)? y/n: ")

    if api_decision == "y":

        url = "https://api.covid19api.com"

        check_connection(base=url)
        get_countries_list = request_countries(base=url)
        print_countries(c_list=get_countries_list)

        year_data_with_responses = gather_countries(c_list=get_countries_list, base=url)
        # returns: [countries_with_empty_response: list, countries_with_response: list, countries_df: DataFrame]

        empty_response_list = year_data_with_responses[0]
        non_empty_response_list = year_data_with_responses[1]
        world = year_data_with_responses[2]

        day_by_day_period_1 = make_period(from_data=[2020, 4, 1], to_date=[2021, 3, 30])
        day_by_day_period_2 = make_period(from_data=[2020, 4, 2], to_date=[2021, 3, 31])

        united_states = gather_day_by_day(periods_1=day_by_day_period_1, periods_2=day_by_day_period_2, base=url)
        update_to_non_empty_response(non_empty=non_empty_response_list,
                                     empty=empty_response_list,
                                     item="united-states")

        api_data = join_countries(df1=world, df2=united_states)

    elif api_decision == "n":
        try:
            api_data = load_csv_skip_api(path="data/world_and_usa_df.csv")
        except Exception as e:
            print("Error has occurred: ", e, "\n")

    else:
        print("Nothing to do here, go home")

    # ----------------TOP 10 countries in the last month----------------
    input("Press ENTER to continue viewing TOP 10 countries in the last month: \n")

    for cat in ["Recovered", "Confirmed", "Deaths"]:
        masked_data = mask_date(data=api_data, category=cat, date_from="2021-3-1", date_to="2021-3-31")
        absolute_data = count_absolute_difference(data=masked_data, category=cat, row_limit=5889)
        arranged_data = group_sum_sort(data=absolute_data, category=cat)
        print(arranged_data)
        plot_category(data=arranged_data, category=cat)

    # ----------------Last month in Poland----------------
    input("Press ENTER to continue viewing Last month in Poland: \n")

    poland_df = choose_country(data=api_data, country="Poland")
    masked_poland = mask_date(data=poland_df, date_from="2021-3-1", date_to="2021-3-31")
    poland_no_outlier = outlier_for_active_category(data=masked_poland)
    print(poland_no_outlier)
    plot_categories(data=poland_no_outlier, x_ticks=True, y_ticks=True)

    # ----------------Monthly growth----------------
    input("Press ENTER to continue viewing Monthly growth: \n")

    stripped_monthly_data = strip_date(data=api_data, category="Recovered")
    absolute_monthly_data = count_absolute_difference(data=stripped_monthly_data, category="Recovered", row_limit=2279)
    sorted_monthly_data = group_sum_sort2(data=absolute_monthly_data, category="Recovered")
    print(sorted_monthly_data)
    category_increment_plot(data=sorted_monthly_data, category="Recovered", x_ticks=True)


def check_connection(base: str) -> None:
    """
    Checks connection to the base and prints html response status code.
        Parameters:
            base (str): url to the API. i.e."https://api.covid19api.com"
        Returns: None
    """

    try:
        response = requests.get(base)
        print(response, "Connection is fine!\n")
    except Exception as e:
        print("Error has occurred: ", e, "\n")


def request_countries(base: str, show_response: bool = False) -> list:
    """
    Makes requests to take list of countries.
            Parameters:
                base (str): url to the API. i.e."https://api.covid19api.com"
                show_response: (bool): Show HTML status code. (Default: False)
            Returns: countries_list (list)
    """

    response = requests.get(base + "/countries")

    if show_response:
        print(response)

    countries_json = response.json()
    countries_list = []

    for item in countries_json:
        # my_list = []
        my_list = item.get('Slug')
        countries_list.append(my_list)

    return countries_list


def print_countries(c_list: list) -> None:
    """
    Prints out list of countries (with length of this list) inline with comma separator.
            Parameters:
                c_list (list): Countries list taken from API
            Returns: None
    """

    data = c_list
    print("Number of all countries: ", len(data))
    print(*data, "\n", sep=", ")


def gather_countries(c_list: list, base: str, save: bool = False) -> list:
    """
    Gathers [Country, Confirmed, Deaths, Recovered, Active, Date] from API requests and builds DataFrame. Also makes
    lists of countries with successful response and not successful response.
            Parameters:
                c_list (list): Countries list taken from API
                base (str): url to the API. i.e."https://api.covid19api.com"
                save (bool): Saves DataFrame to csv file in /data directory. (Default: False)
            Returns: [countries_with_empty_response, countries_with_response, countries_df] (list)
    """

    data = c_list
    countries_with_empty_response = []
    countries_with_response = []
    countries_data_list = []

    for country in data:
        response = requests.get(base + '/country/' + country + '?from=2020-04-01T00:00:00Z&to=2021-03-31T00:00:00Z')
        country_response = response.json()

        if len(country_response) <= 2:
            countries_with_empty_response.append(country)
            # continue
        else:
            countries_with_response.append(country)

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

    countries_data_json = json.dumps(countries_data_list)
    countries_df = pd.read_json(countries_data_json)

    if save:
        countries_df.to_csv('data/countries_df.csv', index=False)

    return [countries_with_empty_response, countries_with_response, countries_df]


def make_period(from_data: list, to_date: list) -> list:
    """
    Creates two lists with dates differing by a day.
        Parameters:
            from_data (list): [yyyy, m, d] format is necessary. e.g. from_data=[2020, 4, 1],
            to_date (list): [yyyy, m, d] format is necessary. e.g. to_date=[2021, 3, 30].
        Returns: dates_list (list)
    """

    start_date = datetime.date(from_data[0], from_data[1], from_data[2])
    end_date = datetime.date(to_date[0], to_date[1], to_date[2])
    delta = datetime.timedelta(days=1)

    dates_list = []

    while start_date <= end_date:
        dates_list.append(start_date)
        start_date += delta

    return dates_list


def gather_day_by_day(periods_1: list, periods_2: list, base: str, save: bool = False) -> pd.DataFrame:
    """
    Gathers [Country, Confirmed, Deaths, Recovered, Active, Date] from API requests and builds DataFrame.
    Only for united-states.
            Parameters:
                periods_1 (list): List of dates in yyyy-m-d format. Should be == len (periods_2).
                periods_2 (list): List of dates in yyyy-m-d format. Should be == len (periods_1).
                base (str): url to the API. i.e."https://api.covid19api.com"
                save (bool): Saves DataFrame to csv file in /data directory. (Default: False)
            Returns: country_usa_df (pd.DataFrame)
    """

    usa_data_list = []

    for from_date, to_date in zip(periods_1, periods_2):
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

    usa_data = json.dumps(usa_data_list)
    country_usa_df = pd.read_json(usa_data)

    if save:
        country_usa_df.to_csv('data/country_usa_df.csv', index=False)

    return country_usa_df


def update_to_non_empty_response(non_empty: list, empty: list, item: str = "united-states") -> list:
    """
    Takes non-empty and empty lists, append non empty, and remove element from empty with item.
            Parameters:
                non_empty (list): List of countries with correct response.
                empty (list): List of countries with no response.
                item (str): Name of country from API's slug. (Default: "united-states").
            Returns: [non_empty, empty] (list)
    """

    non_empty.append(item)
    print("Number of countries with data: ", len(non_empty))
    print(*non_empty, "\n", sep=", ")

    empty.remove(item)
    print("Number of countries without data: ", len(empty))
    print(*empty, "\n", sep=", ")

    return [non_empty, empty]


def join_countries(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """
     Joins two DataFrames. Saves it to csv file in /data directory.
        Parameters:
            df1 (pd.DataFrame): DataFrame with all countries with correct response.
            df2 (pd.DataFrame):  DataFrame united-states data.
        Returns: countries_and_usa_df (pd.DataFrame)
    """

    countries_and_usa_df = df1.append(df2)
    countries_and_usa_df.to_csv('data/world_and_usa_df.csv', index=False)
    print("Finished dataframe:\n", countries_and_usa_df)

    return countries_and_usa_df


def load_csv_skip_api(path: str = "data/world_and_usa_df.csv") -> pd.DataFrame:
    """
    Save 20 minutes of your life, skip api, load csv.
        Parameters:
            path (str): Absolute path to folder with csv file. (Default: "data/world_and_usa_df.csv")
        Returns: data (pd.DataFrame)
    """

    data = pd.read_csv(path)
    print("Data successfully loaded to 'api_data' variable!")

    return data


def mask_date(data: pd.DataFrame, date_from: str, date_to: str, category: Optional[str] = None) -> pd.DataFrame:
    """
    Masks data with timeframe. Optional for indicated category.
            Parameters:
                data (pd.DataFrame): Data to manipulate.
                date_from (str): Date in yyyy-m-d format. e.g. date_from="2021-3-1"
                date_to (str): Date in yyyy-m-d format. e.g. date_to="2021-3-31"
                category (str): OPTIONAL. Column with category: "Recovered", "Confirmed", "Deaths", "Active".
            Returns: masked_df (pd.DataFrame)
    """

    if category:
        masked_df = data[['Country', category, 'Date']]
    else:
        masked_df = data

    masked_df['Date'] = masked_df['Date'].astype(str).str[:10]
    masked_df['Date'] = pd.to_datetime(masked_df['Date'])

    date_mask = (masked_df['Date'] >= date_from) & (masked_df['Date'] <= date_to)
    masked_df = masked_df.loc[date_mask]

    masked_df.reset_index(drop=True, inplace=True)

    return masked_df


def count_absolute_difference(data: pd.DataFrame, category: str, row_limit: int) -> pd.DataFrame:
    """
    Assigns value as absolute difference of second row for category minus first row for test.
    (Test is a copy of category column).
            Parameters:
                data (pd.DataFrame): Data to manipulate.
                category (str): Column with category: "Recovered", "Confirmed", "Deaths", "Active".
                row_limit (int): Length of used DataFrame. e.g.: 5889 or 2279
            Returns: absolute_df (pd.DataFrame)
    """

    absolute_df = data[['Country', 'Date', category]].groupby(['Country', 'Date']).sum()
    absolute_df.reset_index(inplace=True)

    absolute_df['Test'] = absolute_df[category]
    absolute_df[f'{category}_increment'] = 0
    # absolute_df

    # 1 month limit means records for 1 country from last month
    month_limit = 30
    df_limit = row_limit
    index_counter = 0

    while month_limit <= df_limit:

        while index_counter <= month_limit and index_counter <= df_limit:
            if index_counter == df_limit:
                break
            else:
                # assigned value is our absolute difference = second row for category - first row for test
                # (test is a copy of category). To better understanding uncomment 'absolute_df'
                absolute_df[f'{category}_increment'][index_counter + 1] = absolute_df[category][index_counter + 1] - \
                                                                          absolute_df['Test'][index_counter]
                index_counter += 1

        if index_counter >= month_limit:
            month_limit += 31

    return absolute_df


def group_sum_sort(data: pd.DataFrame, category: str) -> pd.DataFrame:
    """
    Slices data to Country, {category}_increment and Date. Groups by Country, sum and sort descending by 10.
            Parameters:
                data (pd.DataFrame): Data to manipulate.
                category (str): Column with category: "Recovered", "Confirmed", "Deaths", "Active".
            Returns: group_sum_sort_df (pd.DataFrame)
    """

    group_sum_sort_df = data[['Country', f'{category}_increment', 'Date']]

    group_sum_sort_df = group_sum_sort_df.groupby(by="Country").sum()
    group_sum_sort_df = group_sum_sort_df.sort_values(by=f'{category}_increment', ascending=False).head(10)

    return group_sum_sort_df


def plot_category(data: pd.DataFrame, category: str) -> plt:
    """
    Plots bar plot with dates on x-axis, and {category}_increment on y-axis.
            Parameters:
                data (pd.DataFrame): Data to plot.
                category (str): Column with category: "Recovered", "Confirmed", "Deaths", "Active".
            Returns: plot (plt)
    """

    plt.figure(figsize=(10, 7))
    sns.barplot(x=data.index, y=f'{category}_increment', data=data)
    plt.title(f"TOP 10 countries with the highest number of {category} cases in the last month")
    plt.xticks(rotation=45)
    plt.grid()

    plt.tight_layout()

    return plt.show()


def choose_country(data: pd.DataFrame, country: str) -> pd.DataFrame:
    """
    Slices DataFrame to only one chosen country.
            Parameters:
                data (pd.DataFrame): Data to manipulate.
                country (str): Name of country from API's slug. e.g. "Poland"
            Returns: country_df (pd.DataFrame)
    """

    country_df = data.loc[data["Country"] == country]
    country_df.reset_index(drop=True, inplace=True)

    return country_df


def outlier_for_active_category(data: pd.DataFrame) -> pd.DataFrame:
    """
    Locate outliers above 1e6 and recalculate it.
            Parameters:
                data (pd.DataFrame): Data to manipulate.
            Returns: data (pd.DataFrame)
    """
    try:
        idx = data.index[data['Active'] > 1e6].tolist()
        data.iloc[idx[0], 4] = data.iloc[idx[0], 1] - data.iloc[idx[0], 2] - data.iloc[idx[0], 3]
    except Exception as e:
        print(f"Error has occurred: {e}. In this case there's no more outliers in active category.")

    return data


def plot_categories(data: pd.DataFrame, x_ticks: bool = False, y_ticks: bool = False) -> plt:
    """
    Plots four subplots (line plots) with dates on x-axis, and four categories on y-axis
            Parameters:
                data (pd.DataFrame): Data to plot.
                x_ticks (bool): Rotation on x axis (90 degrees) and more dates. (Default: False)
                y_ticks (bool): Y-axis range ticks. (Default: False)
            Returns: plot (plt)
    """

    fig, axes = plt.subplots(4, 1, figsize=(12, 9), sharex="all")

    plt.suptitle("Statistics for Poland for the last month", fontsize=14)

    sns.lineplot(ax=axes[0], data=data, x='Date', y='Confirmed', color='orange', linewidth=2)
    axes[0].set_title("Confirmed")
    axes[0].grid(True)

    sns.lineplot(ax=axes[1], data=data, x='Date', y='Deaths', color='red', linewidth=2)
    axes[1].set_title("Deaths")
    axes[1].grid(True)

    sns.lineplot(ax=axes[2], data=data, x='Date', y='Recovered', color='green', linewidth=2)
    axes[2].set_title("Recovered")
    axes[2].grid(True)

    sns.lineplot(ax=axes[3], data=data, x='Date', y='Active', color='blue', linewidth=2)
    axes[3].set_title("Active")
    axes[3].grid(True)

    if x_ticks:
        axes[3].tick_params(axis='x', rotation=90)
        axes[3].set_xticks(data['Date'])

    if y_ticks:
        axes[0].set_yticks(range(int(16e5), int(25e5), int(1e5)))
        axes[1].set_yticks(range(42000, 56000, 2000))
        axes[2].set_yticks(range(int(14e5), int(20e5), int(1e5)))
        axes[3].set_yticks(range(200000, 480000, 40000))

    return plt.show()


def strip_date(data: pd.DataFrame, category: Optional[str] = None) -> pd.DataFrame:
    """
    Strip DataFrame's dates to yyyy-mm format.
            Parameters:
                data (pd.DataFrame): Data to manipulate.
                category (str): Column with category: "Recovered", "Confirmed", "Deaths", "Active".
            Returns: data (pd.DataFrame)
    """

    if category:
        stripped_df = data[['Country', category, 'Date']]
    else:
        stripped_df = data

    stripped_df['Date'] = stripped_df['Date'].astype(str).str[:7]

    return stripped_df


def group_sum_sort2(data: pd.DataFrame, category: str) -> pd.DataFrame:
    """
    Slices data to Country, {category}, {category}_increment and Date. Groups by Date, sum and sort ascending.
            Parameters:
                data (pd.DataFrame): Data to manipulate.
                category (str): Column with category: "Recovered", "Confirmed", "Deaths", "Active".
            Returns: group_sum_sort_df (pd.DataFrame)
    """

    group_sort_df = data[['Country', category, f'{category}_increment', 'Date']]
    group_sort_df.loc[group_sort_df[f'{category}_increment'] < 0, f'{category}_increment'] = 0
    group_sort_df = group_sort_df.groupby(by="Date").sum()
    group_sort_df = group_sort_df.sort_values(by='Date', ascending=True)

    return group_sort_df


def category_increment_plot(data: pd.DataFrame, category: str, x_ticks: bool = False) -> plt:
    """
    Plots two line plot with dates on x-axis, and {category}, {category}_increment on y-axis.
            Parameters:
                data (pd.DataFrame): Data to plot.
                category (str): Column with category: "Recovered", "Confirmed", "Deaths", "Active".
                x_ticks (bool): Rotation on x axis (45 degrees). (Default: False)
            Returns: plot (plt)
    """

    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex="all")

    plt.suptitle("Monthly growth in recoveries over the past year", fontsize=12)

    sns.lineplot(ax=axes[0], data=data, x='Date', y=f'{category}_increment', color='red', linewidth=2)
    axes[0].set_title("Increment")
    axes[0].grid(True)

    sns.lineplot(ax=axes[1], data=data, x='Date', y=category, color='green', linewidth=2)
    axes[1].set_title(category)
    axes[1].grid(True)

    if x_ticks:
        axes[1].tick_params(axis='x', rotation=45)

    return plt.show()


if __name__ == "__main__":
    main()
