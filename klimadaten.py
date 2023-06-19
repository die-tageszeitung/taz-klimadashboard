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
    temp_df = pd.read_csv(tempurl, comment ="%", sep="\s+", header=None)
    #temp_df.drop(columns=[3,4,5,6,7,8,9,10,11],inplace=True)
    nodups_df = temp_df[temp_df[[0,1]].duplicated(keep='first')]
    months_df = nodups_df[nodups_df[1] == nodups_df.iloc[-1,[1]][1]]
    preind = months_df[(months_df[0]>=1850) & (months_df[0]<=1900)][2].mean()
    temp = round(months_df.iloc[-1,[2]][2]-preind,2)
    return f"Erderhitzung im {MONTHS[nodups_df.iloc[-1,[1]][1].astype(int).astype(str)]} {months_df.iloc[-1,[0]][0].astype(int)}, +{temp} °C\n"

def seavalue():
    sea_df = pd.read_csv(seaurl, comment ="#")
    sea_df['year']=sea_df['year'].astype(str).str[:4].astype(int)
    means_df = sea_df.groupby('year').mean().mean(axis=1)
    return f"Meeresspiegelanstieg seit 1992, +{round(means_df.iloc[-1]-means_df.iloc[0],2)} mm\n"

with open("data/final/co2.csv","w") as co2File:
    co2File.write(co2value())
    #co2File.write(tempvalue())
    #co2File.write(seavalue())

headers = {"Authorization": TOKEN,"Accept": "*/*"}

response = requests.request("POST", dwurl, headers=headers)

print("Done")
