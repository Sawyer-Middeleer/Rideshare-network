import pandas as pd
import numpy as np
import geopandas as gpd
import os
import random
import datetime as dt
import re
import matplotlib.pyplot as plt
import seaborn as sns
from sodapy import Socrata
from urllib.request import Request, urlopen
from numpy.polynomial.polynomial import polyfit

wd = os.getcwd()

# construct dataset based on random samples drawn from original datasets

# tnc_file_loc = r'C:\Users\midde\OneDrive\Documents\UChicago Harris\Urban Economics\TNC_Trips'
# np.random.seed(233)
#
# chi_trips = pd.DataFrame()
#
# # get random subset of 5% of rows from each 50k-row dataframe
#
# for i in range(1, 2016):
#     try:
#         trips_df = pd.read_csv(tnc_file_loc+r'\chi_trips_{}.csv'.format(i))
#         sample_indeces = random.sample(range(1, len(trips_df)), int(0.05*len(trips_df)))
#         trips_subset = trips_df[trips_df.index.isin(sample_indeces)]
#
#         chi_trips = chi_trips.append(trips_subset, ignore_index=True)
#         print(i)
#     except:
#         pass
#         print('oops, '+ str(i))
#     if i == 2015:
#         print('done')
#
# chi_trips.to_csv('chi_trips_sample.csv', index=False)

# read data
tnc_trips = pd.read_csv('chi_trips_sample.csv')
cta_daily_entries = pd.read_csv('CTA_Station_Entries_Daily_Totals.csv')
cca_data = pd.read_csv('ReferenceCCAProfiles20132017.csv')
cas = gpd.read_file('Boundaries_Community_Areas.geojson')
cta_stations = gpd.read_file(r'C:\Users\midde\OneDrive\Documents\GitHub\Rideshare-network-analysis\CTA_RailStations\CTA_RailStations.shp')

cas['area_num_1'] = cas['area_num_1'].astype(int)
tnc_trips = tnc_trips.merge(cas, how='left', left_on='pickup_community_area', right_on='area_num_1')


list(cca_data.columns)
cca_data[['GEOG', 'MEDINC']]

# for counting convenience
tnc_trips['dummy'] = 1

# for time series analysis
tnc_trips['trip_start_timestamp'] = pd.to_datetime(tnc_trips['trip_start_timestamp'])
tnc_trips = tnc_trips.set_index('trip_start_timestamp')
tnc_trips['year'] = tnc_trips.index.year
tnc_trips['month'] = tnc_trips.index.month
tnc_trips['day'] = tnc_trips.index.weekday_name
tnc_trips['date'] = tnc_trips.index.date



def fix_type(df, dict):
    for key in dict:
        df[key] = pd.to_numeric(df[key], errors='coerce')
        df = df.dropna(subset=[key])
        df[key] = df[key].astype(dict[key])
    return df



def delta(x, y):
    try:
        return (y-x)/x
    except:
        pass

def divide(x, y):
    try:
        return x/y
    except:
        pass



def basic_map(geo_df, variable, title):
    fig, ax = plt.subplots(1, 1, figsize=(20,10))
    ax.axis('off')
    fig.suptitle(title,
                 fontsize='18')
    geo_df.plot(column=variable,
            ax=ax,
            scheme='quantiles',
            cmap='Blues',
            edgecolor='gray',
            legend=True,
            legend_kwds={'loc': 'lower left'})



def resampled_chart(df, variable, title, start, end, t1='D', t2=None, t3=None, sum=False, mean=False):
    if sum:
        df1 = df[[variable]].resample(t1).sum()
        if t2 is not None:
            df2 = df[[variable]].resample(t2).sum()
        if t3 is not None:
            df3 = df[[variable]].resample(t3).sum()
    elif mean:
        df1 = df[[variable]].resample(t1).mean()
        if t2 is not None:
            df2 = df[[variable]].resample(t2).mean()
        if t3 is not None:
            df3 = df[[variable]].resample(t3).mean()
    else:
        return False

    fig, ax = plt.subplots(1, 1, figsize=(20,10))

    ax.plot(df1.loc[start:end, variable],
    marker='.', linestyle='-', linewidth=0.5, label='{}'.format(t1))

    if t2 is not None:
        ax.plot(df2.loc[start:end, variable],
        marker='o', markersize=8, linewidth=0.75, linestyle='-', label='{}'.format(t2))
    if t3 is not None:
        ax.plot(df3.loc[start:end, variable],
        marker='s', markersize=8, linestyle='-', label='{}'.format(t3))

    ax.set_ylabel(title)
    ax.legend();


vars_to_fix = {'fare': int,
               'trip_total': int,
               'tip': float,
               'pickup_community_area': int,
               'dropoff_community_area': int,
               }

tnc_trips = fix_type(tnc_trips, vars_to_fix)

# new variables
tnc_trips['price_per_mile'] = np.divide(tnc_trips['trip_total'], tnc_trips['trip_miles'])
tnc_trips = tnc_trips.loc[tnc_trips['price_per_mile'] < 50]

# Some quick charts

tnc_f = tnc_trips.loc[tnc_trips['fare'] <= 50] # only rides below $50
sns.distplot(tnc_f['fare'], kde=False) # plot fares

len(tnc_trips.loc[tnc_trips['shared_trip_authorized'] == True]) / len(tnc_trips) # 22.7% of rides are shared


# Mapping

# fares
tnc_trips_19 = tnc_trips[tnc_trips['year'] == 2019]
tnc_fares = tnc_trips_19.groupby([tnc_trips_19['community']]).mean()
tnc_fares_geo = gpd.GeoDataFrame(tnc_fares.merge(cas))
basic_map(tnc_fares_geo, 'trip_total', 'Mean Total Rideshare Fare Amount \n by Origin Neighborhood, 2019')

# trips
tnc_trips_19 = tnc_trips[tnc_trips['year'] == 2019]
tnc_trips_1909 = tnc_trips_19[tnc_trips_19['month'] == 9]
tnc_trips_1909 = tnc_trips_1909.groupby([tnc_trips_1909['community']]).sum()
tnc_trips_geo = gpd.GeoDataFrame(tnc_trips_1909.reset_index().merge(cas, on='community'))
tnc_trips_geo
basic_map(tnc_trips_geo, 'dummy', 'Total TNC Rides, Sept. 2019')

# filter by time of day, group by day of week, etc
# Map change in tnc ridership by community area over time (11-2018 - 9-2019)
# share pooled by community area


# charts
resampled_chart(tnc_trips, 'dummy', 'Number of Rides', '2018-11', '2019-09-01', t1='H', t2='D', t3='W', sum=True)
resampled_chart(tnc_trips, 'trip_total', 'Average Prices', '2018-11', '2019-09', t1='D', t2='W', t3='M', mean=True)
resampled_chart(tnc_trips, 'trip_miles', 'Average Ride Distance (miles)', '2018-11', '2019-09', t1='D', t2='W', t3='M', mean=True)
resampled_chart(tnc_trips, 'price_per_mile', 'Average Ride Price Per Mile', '2018-11', '2019-09', t1='D', t2='W', t3='M', mean=True)

cta_daily_entries['station_id'] = cta_daily_entries['station_id'].astype('str')
cta_daily_entries['station_id'] = cta_daily_entries['station_id'].map(lambda x: re.sub('(^40+|^4)', '', x))
cta_daily_entries['station_id'] = cta_daily_entries['station_id'].astype('int')

cta_daily_entries['date'] = pd.to_datetime(cta_daily_entries['date'])
cta_daily_entries['date'] = cta_daily_entries['date'] + pd.to_timedelta(cta_daily_entries.groupby('date').cumcount(), unit='s')
cta_daily_entries = cta_daily_entries.set_index('date')

cta_daily_entries['year'] = cta_daily_entries.index.year
cta_daily_entries['month'] = cta_daily_entries.index.month
cta_daily_entries['day'] = cta_daily_entries.index.weekday_name
cta_daily_entries['date'] = cta_daily_entries.index.date


cta_stations = cta_stations.to_crs({'init': 'epsg:4326'})
cca_with_stations = gpd.sjoin(cas, cta_stations, how="left", op='intersects')
cca_with_stations = cca_with_stations.dropna()

cca_with_stations = cca_with_stations.rename(columns={'STATION_ID':'station_id'})
cca_with_stations['station_id'] = cca_with_stations['station_id'].astype('int')


list(cca_with_stations['station_id'].unique())
list(cta_daily_entries['station_id'].unique())

cta_cca_merged = pd.merge(cta_daily_entries, cca_with_stations, how='left')
cta_cca_merged = cta_cca_merged.dropna()
cta_cca_merged['rides'] = cta_cca_merged['rides'].apply(lambda x: x.replace(',', ''))
cta_cca_merged[['rides', 'area_numbe', 'area_num_1', 'comarea_id']] = cta_cca_merged[['rides', 'area_numbe', 'area_num_1', 'comarea_id']].astype(int)

cta_cca_19 = cta_cca_merged.loc[cta_cca_merged.year == 2019]
cta_cca_19 = cta_cca_19.groupby(['community']).sum()
cta_cca_19_geo = gpd.GeoDataFrame(cta_cca_19.reset_index().merge(cas, how='left', on='community'))

tnc_trips_19 = tnc_trips_19.groupby(['community']).sum()

cta_cca_19 = cta_cca_19.merge(tnc_trips_19, how='left', on='community')
cta_cca_19 = pd.DataFrame(cta_cca_19)


b, m = polyfit(cta_cca_19['rides'], cta_cca_19['dummy'], 1)
plt.scatter(cta_cca_19['rides'], cta_cca_19['dummy'])
plt.plot(cta_cca_19['rides'], b + m * cta_cca_19['rides'], '-')



cta_cca_merged['date'] = pd.to_datetime(cta_cca_merged['date'])
cta_cca_merged = cta_cca_merged.set_index('date')
cta_cca_merged = cta_cca_merged.groupby(['date']).sum()


# cta_cca_merged.to_csv('cta_cca_merged.csv', index=False)
# !!!!
# 1) Graph average rides/week and # take transit
# 2) maps of cta stuff and comparisons
# 3) avg % change in weekly ridership for nov 2018 vs sept 2019 by commuity area
# regress all the controll variables (med inc, pct nonwhite, etc.)

# margaret
# Graph %change in weekly tnc rides and %change in community cta boardings
# Filter (all?) 2 by top and bottom 20% income neighborhoods
