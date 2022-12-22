import requests
import pandas as pd
import random as rd
import datetime as dt
import mysql.connector as connector
from sqlalchemy import create_engine

############################# Table ObjetsPerdus #############################

URL = "https://ressources.data.sncf.com/api/records/1.0/search/"

params = {
    "dataset" : "objets-trouves-restitution",
    "rows" : "-1",
    "sort":["date"],
}

response = requests.get(URL, params = params)

data = response.json()

list_data = []

for annee in range (2016, 2022):
    for mois in range(1,13):
        params['refine.date'] = str(annee) + "/" + str(mois)

        response = requests.get(URL, params = params)

        data = response.json()

        for record in data["records"]:
            list_data.append(record)

objet_perdus = []

for objet in list_data:
    try:
        objet_perdus.append(objet["fields"])
    except:
        print('not name')

objets_perdus = pd.DataFrame(objet_perdus)

objets_perdus["date"] = pd.to_datetime(objets_perdus["date"])
objets_perdus.set_index("date", inplace=True)

objets_perdus = objets_perdus.rename(columns={"gc_obo_gare_origine_r_code_uic_c":"id", "gc_obo_gare_origine_r_name":"gare", "gc_obo_type_c":"type_objet", "gc_obo_nature_c":"nature_objet"})

del objets_perdus['gc_obo_nom_recordtype_sc_c']
del objets_perdus['gc_obo_date_heure_restitution_c']

objets_perdus.sort_index()

username = "CodeBenji"
mdp = "Code!12345"
db="sncf_meteo"

engine = create_engine(f"mysql+mysqlconnector://{username}:{mdp}@localhost/{db}", echo=True)

objets_perdus.to_sql(name='ObjetsPerdus', con=engine, if_exists = 'replace', index=True)

conn = connector.connect(
  host="localhost",
  user="CodeBenji",
  password="Code!12345",
  database="sncf_meteo"
)

############################# Table Frequentations #############################

URL = "https://ressources.data.sncf.com/api/records/1.0/search/"

params = {
    "dataset" : "frequentation-gares",
    "rows" : "-1",
}

response = requests.get(URL, params = params)

data = response.json()

list_data = []

list_data = []
response = requests.get(URL, params = params)
data = response.json()
for record in data["records"]:
            list_data.append(record)

            
frequentation = []

for gare in list_data:
    try:
        frequentation.append(gare["fields"])
    except:
        print('not name')

frequentations = pd.DataFrame(frequentation)

frequentations.drop(['total_voyageurs_non_voyageurs_2015', 'total_voyageurs_2015'], axis=1, inplace=True)

frequentations['region'] = frequentations['code_postal'].apply(lambda x : x[:2])

frequentations['voyageurs_2016'] = frequentations['total_voyageurs_2016'] + frequentations['total_voyageurs_non_voyageurs_2016']
frequentations.drop(['segmentation_drg', 'total_voyageurs_non_voyageurs_2016', 'total_voyageurs_2016'], axis=1, inplace=True)

frequentations['voyageurs_2017'] = frequentations['totalvoyageurs2017'] + frequentations['total_voyageurs_non_voyageurs_2017']
frequentations.drop(['total_voyageurs_non_voyageurs_2017', 'totalvoyageurs2017'], axis=1, inplace=True)

frequentations['voyageurs_2018'] = frequentations['total_voyageurs_2018'] + frequentations['total_voyageurs_non_voyageurs_2018']
frequentations.drop(['total_voyageurs_non_voyageurs_2018', 'total_voyageurs_2018'], axis=1, inplace=True)

frequentations['voyageurs_2019'] = frequentations['total_voyageurs_2019'] + frequentations['total_voyageurs_non_voyageurs_2019']
frequentations.drop(['total_voyageurs_non_voyageurs_2019', 'total_voyageurs_2019'], axis=1, inplace=True)

frequentations['voyageurs_2020'] = frequentations['total_voyageurs_2020'] + frequentations['total_voyageurs_non_voyageurs_2020']
frequentations.drop(['total_voyageurs_non_voyageurs_2020', 'total_voyageurs_2020'], axis=1, inplace=True)

frequentations['voyageurs_2021'] = frequentations['total_voyageurs_2021'] + frequentations['total_voyageurs_non_voyageurs_2021']
frequentations.drop(['total_voyageurs_non_voyageurs_2021', 'total_voyageurs_2021'], axis=1, inplace=True)

frequentations.rename(columns={"code_uic_complet":"id_gare"}, inplace=True)


annees = list(range(2016,2022))
month = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

for annee in annees:
    for mois in month:
        frequentations[f"{annee}_{mois}"] = frequentations[f"voyageurs_{annee}"]

frequentations.drop(['voyageurs_2016', 'voyageurs_2017', 'voyageurs_2018', 'voyageurs_2019', 'voyageurs_2020', 'voyageurs_2021'], axis=1, inplace=True)

df_trains = pd.read_sql("SELECT * FROM Trains", conn)

df_trains.set_index('date', inplace=True)

del df_trains['total_trains']

annees = list(range(2016,2022))

for annee in annees:
    for mois in month:
        if annee == 2016 or annee == 2017:
            frequentations[f"{annee}_{mois}"] = frequentations[f"{annee}_{mois}"].apply(lambda x: round(x / 12))
        else:
            frequentations[f"{annee}_{mois}"] = frequentations[f"{annee}_{mois}"].apply(lambda x: round(x * df_trains['norme'][f"{annee}_{mois}"] / 12))


frequentations.to_sql(name='Frequentations', con=engine, if_exists = 'replace', index=False)


############################# Table Meteos #############################

meteo = pd.read_csv("agregated_temperature.csv")

meteo.to_sql(name='Meteos', con=engine, if_exists = 'replace', index=False)