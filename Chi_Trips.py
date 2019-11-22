import pandas as pd
import numpy as np
import geopandas as gpd
import os
import random
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
from sodapy import Socrata
from urllib.request import Request, urlopen

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

tnc_trips = pd.read_csv('chi_trips_sample.csv')
cta_daily_entries = pd.read_csv('CTA_Station_Entries_Daily_Totals.csv')
cca_data = pd.read_csv('ReferenceCCAProfiles20132017.csv')
cca_data

tnc_trips['trip_start_timestamp'] = pd.to_datetime(tnc_trips['trip_start_timestamp'])

tnc_trips['fare'] = pd.to_numeric(tnc_trips['fare'], errors='coerce')
tnc_trips = tnc_trips.dropna(subset=['fare'])
tnc_trips['fare'] = tnc_trips['fare'].astype(float)

tnc_trips['pickup_community_area'] = pd.to_numeric(tnc_trips['pickup_community_area'], errors='coerce')
tnc_trips = tnc_trips.dropna(subset=['pickup_community_area'])
tnc_trips['pickup_community_area'] = tnc_trips['pickup_community_area'].astype(int)

tnc_trips['dropoff_community_area'] = pd.to_numeric(tnc_trips['dropoff_community_area'], errors='coerce')
tnc_trips = tnc_trips.dropna(subset=['dropoff_community_area'])
tnc_trips['dropoff_community_area'] = tnc_trips['dropoff_community_area'].astype(int)

tnc_trips['tip'] = pd.to_numeric(tnc_trips['tip'], errors='coerce')
tnc_trips = tnc_trips.dropna(subset=['dropoff_community_area'])
tnc_trips['tip'] = tnc_trips['tip'].astype(float)

tnc_trips['trip_total'] = pd.to_numeric(tnc_trips['trip_total'], errors='coerce')
tnc_trips = tnc_trips.dropna(subset=['trip_total'])
tnc_trips['trip_total'] = tnc_trips['trip_total'].astype(float)

# look at distributions of days, fares, frequencies of rides, etc.

tnc_f = tnc_trips.loc[tnc_trips['fare'] <= 50] # only rides below $50
sns.distplot(tnc_f['fare'], kde=False) # plot fares

tnc_trips.columns

len(tnc_trips.loc[tnc_trips['shared_trip_authorized'] == True]) / len(tnc_trips) # 22.7% of rides are shared
# tnc_g  = tnc_trips.groupby([tnc_trips['trip_start_timestamp'].dt.dayofweek, tnc_trips['shared_trip_authorized']]).sum()

tnc_g  = tnc_trips.groupby([tnc_trips['pickup_community_area']]).sum() # by community area
plt.bar(tnc_g.index, tnc_g['trips_pooled'])



# Mapping
cas = gpd.read_file('Boundaries_Community_Areas.geojson')

cas['area_num_1'] = cas['area_num_1'].astype(int)

tnc_trips = tnc_trips.merge(cas, how='left', left_on='pickup_community_area', right_on='area_num_1')

# calculate new columns (fare/median-income, tip/fare or something)
# filter by time of day, group by day of week, etc

def delta(x, y):
    return (y-x)/x

def divide(x, y):
    try:
        return x/y
    except:
        pass


tnc_tip_prop = tnc_trips.groupby(['community']).apply(lambda x: len(x[x['tip'] > 0])/len(x))
tnc_tip_prop = pd.DataFrame({'Proportion_Tipped': tnc_tip_prop})
tnc_tip_prop = tnc_tip_prop.reset_index()
tnc_tip_prop_geo = gpd.GeoDataFrame(tnc_tip_prop.merge(cas))

fig, ax = plt.subplots(1, 1, figsize=(20,10))
ax.axis('off')
fig.suptitle('Proportion of Rides Tipped by Origin Community Area',
             fontsize='18')
tnc_tip_prop_geo.plot(column='Proportion_Tipped',
                   ax=ax,
                   scheme='quantiles',
                   cmap='Blues',
                   edgecolor='gray',
                   legend=True,
                   legend_kwds={'loc': 'lower left'})



tnc_trips_19 = tnc_trips[tnc_trips['trip_start_timestamp'].dt.year == 2019]
tnc_fares = tnc_trips_19.groupby([tnc_trips_19['community']]).mean()

tnc_fares_geo = gpd.GeoDataFrame(tnc_fares.merge(cas))

fig, ax = plt.subplots(1, 1, figsize=(20,10))
ax.axis('off')
fig.suptitle('Mean Total Rideshare Fare Amount \n by Origin Neighborhood, 2019',
             fontsize='18')
tnc_fares_geo.plot(column='trip_total',
                   ax=ax,
                   scheme='quantiles',
                   cmap='Blues',
                   edgecolor='gray',
                   legend=True,
                   legend_kwds={'loc': 'lower left'})

list(cca_data.columns)
cca_data[['DROVE_AL', 'CARPOOL', 'TRANSIT', 'WALK_BIKE', 'COMM_OTHER']]


# time series analysis
tnc_trips = tnc_trips.set_index('trip_start_timestamp')
tnc_trips['year'] = tnc_trips.index.year
tnc_trips['month'] = tnc_trips.index.month
tnc_trips['day'] = tnc_trips.index.weekday_name
tnc_trips['date'] = tnc_trips.index.date

# Map change in tnc ridership by community area over time (11-2018 - 9-2019)
tnc_trips['dummy'] = 1
# daily, weekly, monthly rides numbers

tnc_trips_daily = tnc_trips[['dummy']].resample('D').sum()
tnc_trips_weekly = tnc_trips[['dummy']].resample('W').sum()
tnc_trips_monthly = tnc_trips[['dummy']].resample('M').sum()

start, end = '2018-11-01', '2019-09-30'

fig, ax = plt.subplots(1, 1, figsize=(20,10))
ax.plot(tnc_trips_daily.loc[start:end, 'dummy'],
marker='.', linestyle='-', linewidth=0.5, label='Daily Rides')
ax.plot(tnc_trips_weekly.loc[start:end, 'dummy'],
marker='o', markersize=8, linestyle='-', label='Weekly Rides')
ax.plot(tnc_trips_monthly.loc[start:end, 'dummy'],
marker='s', markersize=8, linestyle='-', label='Monthly Rides')
ax.set_ylabel('Number of Rides')
ax.legend();

# daily, weekly, monthly average price

tnc_price_daily = tnc_trips[['trip_total']].resample('D').mean()
tnc_price_weekly = tnc_trips[['trip_total']].resample('W').mean()
tnc_price_monthly = tnc_trips[['trip_total']].resample('M').mean()

start, end = '2018-11-01', '2019-09-30'

fig, ax = plt.subplots(1, 1, figsize=(20,10))
ax.plot(tnc_price_daily.loc[start:end, 'trip_total'],
marker='.', linestyle='-', linewidth=0.5, label='Daily Ride Prices')
ax.plot(tnc_price_weekly.loc[start:end, 'trip_total'],
marker='o', markersize=8, linestyle='-', label='Weekly Ride Prices')
ax.plot(tnc_price_monthly.loc[start:end, 'trip_total'],
marker='s', markersize=8, linestyle='-', label='Monthly Ride Prices')
ax.set_ylabel('Average Ride Price')
ax.legend();

# daily, weekly, monthly average distance

tnc_dist_daily = tnc_trips[['trip_miles']].resample('D').mean()
tnc_dist_weekly = tnc_trips[['trip_miles']].resample('W').mean()
tnc_dist_monthly = tnc_trips[['trip_miles']].resample('M').mean()

start, end = '2018-11-01', '2019-09-30'

fig, ax = plt.subplots(1, 1, figsize=(20,10))
ax.plot(tnc_dist_daily.loc[start:end, 'trip_miles'],
marker='.', linestyle='-', linewidth=0.5, label='Daily Ride Distance')
ax.plot(tnc_dist_weekly.loc[start:end, 'trip_miles'],
marker='o', markersize=8, linestyle='-', label='Weekly Ride Distance')
ax.plot(tnc_dist_monthly.loc[start:end, 'trip_miles'],
marker='s', markersize=8, linestyle='-', label='Monthly Ride Distance')
ax.set_ylabel('Average Ride Distance (miles)')
ax.legend();

# daily, weekly, monthly average time

tnc_dur_daily = tnc_trips[['trip_seconds']].resample('D').mean()
tnc_dur_weekly = tnc_trips[['trip_seconds']].resample('W').mean()
tnc_dur_monthly = tnc_trips[['trip_seconds']].resample('M').mean()

start, end = '2018-11-01', '2019-09-30'

fig, ax = plt.subplots(1, 1, figsize=(20,10))
ax.plot(tnc_dur_daily.loc[start:end, 'trip_seconds'],
marker='.', linestyle='-', linewidth=0.5, label='Daily Ride Duration')
ax.plot(tnc_dur_weekly.loc[start:end, 'trip_seconds'],
marker='o', markersize=8, linestyle='-', label='Weekly Ride Duration')
ax.plot(tnc_dur_monthly.loc[start:end, 'trip_seconds'],
marker='s', markersize=8, linestyle='-', label='Monthly Ride Duration')
ax.set_ylabel('Average Ride Duration (seconds)')
ax.legend();


# DO PRICE PER MILE OR PRICE PER SECOND


#### https://www.dataquest.io/blog/tutorial-time-series-analysis-with-pandas/
# Map average month-over-month ridership by community area
# Graph average rides/week and # take transit



# Graph %change in weekly tnc rides and %change in community cta boardings

# Filter (all?) 2 by top and bottom 20% income neighborhoods
#
