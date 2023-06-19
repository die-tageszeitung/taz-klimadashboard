import requests
import pandas as pd
import os

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
tempurl = "http://berkeleyearth.lbl.gov/auto/Global/Land_and_Ocean_complete.txt"
seaurl = "https://www.star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/slr/slr_sla_gbl_free_txj1j2_90.csv"

def co2value():
    co2_df = pd.read_csv(co2url, comment ="#")
    current_values = co2_df.iloc[-1]
    todays_date = f"{int(current_values['day'])}.{int(current_values['month'])}.{int(current_values['year'])}"
    return f"CO2 in der Atmosphäre am {todays_date}, {current_values['trend']} ppm\n"

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
  temp = round(df_current.iloc[-1]['anomaly'],2)
  date = df_current.iloc[-1]['date'].strftime('%d.%m')
  return f"Erderhitzung am {date}, +{temp} °C\n"

def seavalue():
    sea_df = pd.read_csv(seaurl, comment ="#")
    sea_df['year']=sea_df['year'].astype(str).str[:4].astype(int)
    means_df = sea_df.groupby('year').mean().mean(axis=1)
    return f"Meeresspiegelanstieg seit 1992, +{round(means_df.iloc[-1]-means_df.iloc[0],2)} mm\n"

with open("data/final/co2.csv","w") as co2File:
    co2File.write(co2value())
    co2File.write(tempvalue())
    #co2File.write(seavalue())

headers = {"Authorization": TOKEN,"Accept": "*/*"}

response = requests.request("POST", dwurl, headers=headers)

print("Done")
