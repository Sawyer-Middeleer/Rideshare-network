import pandas as pd
import requests
from sodapy import Socrata

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
# client = Socrata("data.cityofchicago.org", None)


client = Socrata('data.cityofchicago.org',
                 'g7JL0nhe6EdUFQOCY3bEG0kpo',
                  username='sawyerm@uchicago.edu',
                  password='Seishonagon12!')


results = client.get("m6dm-c72p", limit=2000)

# Convert to pandas DataFrameC
results_df = pd.DataFrame.from_records(results)
results_df
