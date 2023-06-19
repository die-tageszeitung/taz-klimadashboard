import requests
import pandas as pd
import os
import math
from datetime import datetime

MONTHS = {"1":"Januar",
          "2":"Februar",
          "3":"März",
          "4": "April",
          "5": "Mai",
          "6": "Juni",
          "7": "Juli",
          "8": "August",
          "9": "September",
          "10": "Oktober",
          "11": "November",
          "12":"Dezember"
          }

TOKEN =  os.environ['DATAWRAPPER_ACCESS_TOKEN']

dwurl = "https://api.datawrapper.de/v3/charts/25Qgy/publish"
co2url= "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_trend_gl.csv"
CE_URL = 'https://climatereanalyzer.org/clim/t2_daily/json/cfsr_world_t2_day.json'
ICE_URL = 'https://www.theice.com/marketdata/DelayedMarkets.shtml'
seaurl = "https://www.star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/slr/slr_sla_gbl_free_txj1j2_90.csv"

# bietet round_half_up, zu nutzen statt der standard round()-Funktion, die zu geraden Zahlen rundet
def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier

def co2value():
    co2_df = pd.read_csv(co2url, comment ="#")
    current_values = co2_df.iloc[-1]
    todays_date = f"{int(current_values['day'])}.{int(current_values['month'])}.{int(current_values['year'])}"
    return f"CO2 in der Atmosphäre am {todays_date}, {current_values['trend']} ppm\n"

def get_carbon_price():
  params = {
      'getHistoricalChartDataAsJson': '',
      'marketId': '5474737',
      'historicalSpan': '3',
  }

  response = requests.get(ICE_URL, params=params)
  current_data = response.json()['bars'][-1]
  price = current_data[1]
  day = datetime.strptime(current_data[0],'%a %b %d %X %Y').strftime('%d.%m.')
  return f"CO2-Preis in der EU am {day}, price} €\n"

def tempvalue():
  response = requests.get(CE_URL)
  raw_data = response.json()
  data = {x['name']:x['data'] for x in raw_data}
  df = pd.DataFrame.from_dict(data, orient='columns')
  current_year = list(df.columns)[-4:-3][0]
  df['date'] =df.index +1
  df['date'] = pd.to_datetime(df['date'].astype(str)+current_year,format='%j%Y')
  df_current = df[['date',current_year,'1979-2000 mean']]
  df_current =  df_current.dropna()
  df_current['anomaly'] = df_current[current_year]-df_current['1979-2000 mean']+0.657
  temp = round_half_up(df_current.iloc[-1]['anomaly'],2)
  date = df_current.iloc[-1]['date'].strftime('%d.%m')
  return f"Erderhitzung am {date}, +{temp} °C\n"

def seavalue():
    sea_df = pd.read_csv(seaurl, comment ="#")
    sea_df['year']=sea_df['year'].astype(str).str[:4].astype(int)
    means_df = sea_df.groupby('year').mean().mean(axis=1)
    return f"Meeresspiegelanstieg seit 1992, +{round(means_df.iloc[-1]-means_df.iloc[0],2)} mm\n"

if __name__ == "__main__":
          with open("data/final/co2.csv","w") as co2File:
              co2File.write(co2value())
              co2File.write(tempvalue())
              co2File.write(get_carbon_price())
          
          headers = {"Authorization": TOKEN,"Accept": "*/*"}
          
          response = requests.request("POST", dwurl, headers=headers)
          
          print("Done")
