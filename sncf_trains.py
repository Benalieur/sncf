import requests
import pandas as pd
import datetime as dt
from sqlalchemy import create_engine
import unicodedata
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()

################################# Dataframe TGV #################################

URL = "https://ressources.data.sncf.com/api/records/1.0/search/"

params = {
    "dataset" : "regularite-mensuelle-tgv-aqst",
    "rows" : "-1",
    "sort":["date"],
}
response = requests.get(URL, params = params)

data = response.json()

list_data_tgv = []

for annee in range (2016, 2022):
    for mois in range(1,13):
        params['refine.date'] = str(annee) + "/" + str(mois)

        response = requests.get(URL, params = params)

        data = response.json()

        for record in data["records"]:
            list_data_tgv.append(record)
train = []

for gare in list_data_tgv:
    try:
        train.append(gare["fields"])
    except:
        print('not name')
trains = pd.DataFrame(train)
trains["date"] = pd.to_datetime(trains["date"])

trains.sort_values('date')

trains.drop(['prct_cause_infra', 'retard_moyen_trains_retard_sup15', 'retard_moyen_tous_trains_arrivee', 'prct_cause_externe', 'prct_cause_gestion_trafic', 'nb_train_retard_arrivee', 'nb_train_retard_sup_15', 'nb_annulation', 'prct_cause_prise_en_charge_voyageurs', 'service', 'nb_train_depart_retard', 'prct_cause_gestion_gare', 'duree_moyenne', 'retard_moyen_depart', 'retard_moyen_tous_trains_depart', 'prct_cause_materiel_roulant', 'commentaires_retard_arrivee', 'gare_arrivee', 'retard_moyen_arrivee', 'nb_train_retard_sup_30', 'nb_train_retard_sup_60'], axis=1, inplace=True)

################################# Dataframe TER #################################

URL = "https://ressources.data.sncf.com/api/records/1.0/search/"

params = {
    "dataset" : "regularite-mensuelle-ter",
    "rows" : "-1",
    "sort":["date"],
}
response = requests.get(URL, params = params)

data = response.json()

list_data_ter = []

for annee in range (2016, 2022):
    for mois in range(1,13):
        params['refine.date'] = str(annee) + "/" + str(mois)

        response = requests.get(URL, params = params)

        data = response.json()

        for record in data["records"]:
            list_data_ter.append(record)
ter = []

for gare in list_data_ter:
    try:
        ter.append(gare["fields"])
    except:
        print('not name')
ters = pd.DataFrame(ter)
ters["date"] = pd.to_datetime(ters["date"])

ters.sort_values('date')

ters.drop(['nombre_de_trains_a_l_heure_pour_un_train_en_retard_a_l_arrivee', 'nombre_de_trains_en_retard_a_l_arrivee', 'taux_de_regularite', 'nombre_de_trains_ayant_circule', 'nombre_de_trains_annules', 'commentaires'], axis=1, inplace=True)


################################# Dataframe INTERCITES #################################


URL = "https://ressources.data.sncf.com/api/records/1.0/search/"

params = {
    "dataset" : "regularite-mensuelle-intercites",
    "rows" : "-1",
    "sort":["date"],
}
response = requests.get(URL, params = params)

data = response.json()

list_data_intercite = []

for annee in range (2016, 2022):
    for mois in range(1,13):
        params['refine.date'] = str(annee) + "/" + str(mois)

        response = requests.get(URL, params = params)

        data = response.json()

        for record in data["records"]:
            list_data_intercite.append(record)
intercite = []

for gare in list_data_intercite:
    try:
        intercite.append(gare["fields"])
    except:
        print('not name')
intercites = pd.DataFrame(intercite)
intercites["date"] = pd.to_datetime(intercites["date"])

intercites.sort_values('date')

intercites.drop(['nombre_de_trains_a_l_heure_pour_un_train_en_retard_a_l_arrivee', 'nombre_de_trains_annules', 'nombre_de_trains_en_retard_a_l_arrivee', 'taux_de_regularite', 'nombre_de_trains_ayant_circule', 'arrivee'], axis=1, inplace=True)


################################# Calculs des trains totaux #################################

intercites['date'] = pd.to_datetime(intercites['date'])

intercites = intercites.set_index('date').resample('M').sum()
intercites.reset_index(inplace=True)
trains['date'] = pd.to_datetime(trains['date'])

trains = trains.set_index('date').resample('M').sum()
trains.reset_index(inplace=True)
ters['date'] = pd.to_datetime(ters['date'])

ters = ters.set_index('date').resample('M').sum()
ters.reset_index(inplace=True)
dfo_trains = pd.merge(trains, intercites, on='date')

df_trains = pd.merge(dfo_trains, intercites, on='date')

df_trains['total_trains'] = df_trains['nb_train_prevu'] + df_trains['nombre_de_trains_programmes_x'] + df_trains['nombre_de_trains_programmes_y']
df_trains.drop(['nb_train_prevu', 'nombre_de_trains_programmes_x', 'nombre_de_trains_programmes_y'], axis=1, inplace=True)
norm = scaler.fit_transform(df_trains[['total_trains']])
df_trains = df_trains.assign(norme=norm)
df_trains['date'] = df_trains['date'].dt.strftime("%Y_%0m")


username = "CodeBenji"
mdp = "Code!12345"
db="sncf_meteo"

engine = create_engine(f"mysql+mysqlconnector://{username}:{mdp}@localhost/{db}", echo=True)

df_trains.to_sql(name='Trains', con=engine, if_exists = 'replace', index=False)