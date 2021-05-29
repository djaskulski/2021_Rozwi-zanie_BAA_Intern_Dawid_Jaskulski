# Covid report for Allegro SUMMER E-XPERIENCE
## Recruitment: Intern - Business Application Administrator
### Jaskulski Dawid

Table of Contents

    * Data preparation
        * List of all countries
        * List of countries with data
        * List of countries without data
        * Data table for indicated countries

    * TOP 10 countries with the highest number of recoveries in the last month
    * TOP 10 countries with the highest number of confirmed new cases in the last month
    * TOP 10 states with the highest number of deaths in the last month
    * Statistics for Poland for the last month
    * Monthly growth in recoveries over the past year for the entire world

* API: https://api.covid19api.com/
* Documentation: https://documenter.getpostman.com/view/10808728/SzS8rjbc#intro

### PROBLEM 1: Obtain data from the API to answer the questions posed.
#### SOLUTION: Extract a list of countries through a specific query. Automate one of the queries to extract all the data needed.

### PROBLEM 2: Notification of string variable assignment.
#### SOLUTION: Mute notifications: pd.set_option('mode.chained_assignment', None)

### PROBLEM 3: API does not respond to all requests correctly. Information about exceeding the limit for a free user.
#### SOLUTION: Reduce the frequency of queries using the time module and the sleep method.

### PROBLEM 4: Excessively long code runtime when debugging manually.
#### SOLUTION: Skip the loop with API queries by writing and loading data directly to and from a csv file.

### PROBLEM 5: The API returns an error about the time interval being too long for the US query.
#### SOLUTION: Create two lists to serve as a one-day interval for the query directed to the API. Use of parallel iteration.

### PROBLEM 6: API does not return data for certain countries.
#### SOLUTION: Probably missing data for these countries.

### PROBLEM 7: The values in the columns are relative values. Each following day is the sum of the previous day's increment and value.
#### SOLUTION: Obtain the absolute number of argument growth in a given month by implementing the small logic.

### PROBLEM 8: Outlier in one of the records.
#### SOLUTION: Manual recalculation based on other columns.
