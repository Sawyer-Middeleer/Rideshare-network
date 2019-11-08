import os
import us
import pandas as pd
import numpy as np
import requests
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from sodapy import Socrata

class ChicagoRides:

    def __init__(self):
        self.TNC_RIDES_API_ENDPOINT = 'https://data.cityofchicago.org/resource/m6dm-c72p.json'
        self.CLIENT = Socrata("data.cityofchicago.org", None)


    def get_rides_data(self):
        rides = self.CLIENT.get("m6dm-c72p", limit=2000)
        rides_df = pd.DataFrame.from_records(rides)
        return rides_df




def main():
    chi_rides = ChicagoRides()



if __name__ == "__main__":
    main()
