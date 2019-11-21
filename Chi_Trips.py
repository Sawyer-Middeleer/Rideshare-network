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

tnc_trips['trip_start_timestamp'] = pd.to_datetime(tnc_trips['trip_start_timestamp'])

tnc_trips['fare'] = pd.to_numeric(tnc_trips['fare'], errors='coerce')
tnc_trips = tnc_trips.dropna(subset=['fare'])
tnc_trips['fare'] = tnc_trips['fare'].astype(int)

tnc_trips['pickup_community_area'] = pd.to_numeric(tnc_trips['pickup_community_area'], errors='coerce')
tnc_trips = tnc_trips.dropna(subset=['pickup_community_area'])
tnc_trips['pickup_community_area'] = tnc_trips['pickup_community_area'].astype(int)

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

tnc_g = tnc_trips.groupby([tnc_trips['community']]).mean()

tnc_trips_geo = gpd.GeoDataFrame(tnc_g.merge(cas))
tnc_trips_geo.columns




fig, ax = plt.subplots(1, 1, figsize=(20,10))
ax.axis('off')
fig.suptitle('Mean Total Rideshare Fare Amount \n by Origin Neighborhood, 2018 - 2019',
             fontsize='18')
tnc_trips_geo.plot(column='trip_total',
                   ax=ax, scheme='quantiles',
                   cmap='Blues',
                   edgecolor='gray',
                   legend=True,
                   legend_kwds={'loc': 'lower left'})
