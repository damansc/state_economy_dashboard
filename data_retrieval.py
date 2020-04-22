import pandas as pd 

# confirmed counts (updated daily)
URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'

state_cnt = (pd.read_csv(URL)
        .drop(['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Admin2'], axis=1))

# state population
state_pop = pd.read_excel('data/census_pop.xlsx', skiprows=3).dropna(axis=0)
state_pop.columns = [str(x) for x in state_pop.columns]
state_pop = state_pop[['Unnamed: 0', '2019']]
state_pop.columns = ['Province_State', 'pop']
state_pop.iloc[:, 0] = state_pop.iloc[:, 0].str.replace('.', '')

# state GDP
state_gdp = pd.read_csv('data/state_gdp.csv', skiprows=4).dropna(axis=0)
state_gdp.columns = ['Fips', 'Province_State', 'gdp']

# state key for mapping
state_key = pd.read_excel('data/state_key.xlsx').dropna()
state_key.columns = ['Province_State', 'Code']
state_key['Province_State'] = (state_key['Province_State']
                               .map(lambda x: x.rstrip()))

# state debt
state_debt = pd.read_csv('data/debt.csv').dropna()
state_debt.columns = ['Province_State', 'debt', 'perCap', 'Pop']


# all data merged
agg_data = (state_key
            .merge(state_pop, on='Province_State')
            .merge(state_gdp, on='Province_State')
            .merge(state_debt[['Province_State', 'debt']], on='Province_State'))

#gdp per capita
#debt per capita
agg_data['gdp'] = round(agg_data['gdp'].map(lambda x: int(x)) * 1000000, 0)
agg_data['debt'] = round(agg_data['debt'] * 1000, 1)
agg_data['gdp_per_cap'] = round((agg_data['gdp'])/ agg_data['pop'], 1)
agg_data['debt_per_cap'] = round((agg_data['debt']) / agg_data['pop'], 1)
agg_data['gdp/debt'] = round(agg_data['gdp_per_cap'] / agg_data['debt_per_cap'], 1)

agg_data.columns = ['State', 'Code', 'pop', 'Fips', 'GDP', 'Debt', 'GDP per Capita', 
                    'Debt per Capita', 'Per Capita GDP/Debt']

# writing to csv file for use in app
agg_data.to_csv('data/aggregated_data.csv', index=False)
