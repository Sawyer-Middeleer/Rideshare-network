import pandas as pd
import numpy as np
import os
import random
import datetime
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

tnc_trips.head()
cta_daily_entries.head()

tnc_trips['trip_start_timestamp'] = pd.to_datetime(tnc_trips['trip_start_timestamp'])

tnc_trips['fare'] = pd.to_numeric(tnc_trips['fare'], errors='coerce')
tnc_trips = tnc_trips.dropna(subset=['fare'])
tnc_trips['fare'] = tnc_trips['fare'].astype(int)


# look at distributions of days, fares, frequencies of rides, etc.

tnc_f = tnc_trips.loc[tnc_trips['fare'] <= 50] # only rides below $50
sns.distplot(tnc_f['fare'], kde=False) # plot fares
