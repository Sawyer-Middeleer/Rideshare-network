import pandas as pd
import requests
import os
from sodapy import Socrata
from urllib.request import Request, urlopen
# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
# socrata2sql package

working_directory = r'C:\Users\midde\OneDrive\Documents\UChicago Harris\Urban Economics\TNC_Trips'

endpoint = 'https://data.cityofchicago.org/resource/m6dm-c72p.csv'
client = Socrata('data.cityofchicago.org',
                 'g7JL0nhe6EdUFQOCY3bEG0kpo',
                 username="sawyerm@uchicago.edu",
                 password="Harukimurakami9!")

client.timeout = 50000

# make empty dataframe
# look at client.get Docs
# can specify row start row end


# df_list = []
def get_trips(start, off_set, increment):

    i = start
    off = off_set
    inc = increment

    for k in range(1880):
        print(i, off)

        try:
            results = client.get('m6dm-c72p', order='trip_start_timestamp DESC', offset=off, limit=50000)
            df = pd.DataFrame(results)

            df.to_csv(working_directory+r'\chi_trips_{}.csv'.format(i), index = False, header=True)

            results = None
            df = None

            off = inc*i
            i = i + 1

        except:
            get_trips(i, off, inc)

get_trips(1838, 0, 50000)


# with open(r'C:\Users\midde\OneDrive\Documents\GitHub\Rideshare-network-analysis\trips_data.csv',"wb") as csv:
#     # https://dzone.com/articles/simple-examples-of-downloading-files-using-python
#     for chunk in req.iter_content(chunk_size=1024):
#          # writing one chunk at a time to pdf file
#          if chunk:
#              csv.write(chunk)
