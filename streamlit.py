import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import mysql.connector as connector
import plotly.express as px
import unicodedata
import scipy as stats
from scipy.stats import f_oneway, chi2_contingency
import streamlit_folium as sf
import folium

############################# Récupération de la Database #############################

conn = connector.connect(
  host="localhost",
  user="CodeBenji",
  password="Code!12345",
  database="sncf_meteo"
)

objets_perdus = pd.read_sql("SELECT * FROM ObjetsPerdus", conn)
objets_perdus2 = pd.read_sql("SELECT * FROM ObjetsPerdus2", conn)
objets_perdus3 = pd.read_sql("SELECT * FROM ObjetsPerdus3", conn)


objets_perdus["date"] = pd.to_datetime(objets_perdus["date"])
objets_perdus.set_index("date", inplace=True)
objets_perdus.sort_index(inplace=True)

############################# Affichage Streamlit #############################

st.set_page_config(layout="wide",
    page_title="Objets Perdus SNCF")

st.title("Objets Perdus SNCF")

option = st.selectbox('', ('Quelle question voulez-vous afficher?', 'Question 1 : Calculez entre 2016 et 2021 la somme du nombre d’objets perdus par semaine.', 'Question 2 : Afficher l’évolution du nombre d’objets perdus sur la période 2016-2021.', "Question 3 : Afficher une carte de France avec le nombre d’objets perdus en fonction de la fréquentation de voyageur de chaque région.", "Question 4 : Afficher le nombre d’objets perdus en fonction de la température", "Question 5 et 6 : Quelle est la médiane du nombre d’objets perdus en fonction de la saison? Est ce que le nombre d’objets perdus est corrélé à la saison?", "Question 7 : Est ce que le type d’objets perdus est corrélé aux mois?"))


if option == 'Quelle question voulez-vous afficher?':

    st.header('Consignes données par le manager : ')
    st.write("Data Scientist à la SNCF, votre manager vous demande de vous pencher sur un sujet particulier, la gestion des objets perdus.\n En effet, chaque jour des dizaines d'objets sont perdus partout en France par les voyageurs, leur gestion est critique au niveau de la satisfaction client. Cependant leur coût de gestion l'est également. On aimerait donc redimensionner au mieux le service en charge de gérer les objets perdus, pour cela il faut pouvoir anticiper de manière précise le volume d'objets perdus chaque jour. Votre manager a une intuition qu'il aimerait vérifier : plus il fait froid plus les voyageurs sont couverts (manteau, écharpe, gant) et donc ils ont plus de probabilité de les oublier. Mais empiler toutes ces couches prend du temps, ce qui pousse aussi à se mettre en retard et dans la précipitation, à oublier d'autres affaires. À l'aide des données de la SNCF et d'autres données, essayez de creuser cette piste.")


elif option == 'Question 1 : Calculez entre 2016 et 2021 la somme du nombre d’objets perdus par semaine.':
    ############ Question 1 ############
    objets_semaine = objets_perdus.groupby(pd.Grouper(freq='W')).count()
    objets_semaine.drop(['id_gare', 'gare', 'nature_objet'], axis=1, inplace=True)
    objets_semaine.rename(columns={"type_objet":"Nombre Objets Perdus"},inplace=True)


    fig1 = sns.histplot(data=objets_semaine)
    fig_semaine = fig1.get_figure()
    fig_semaine.set_size_inches(8, 4)


    col1, col2 = st.columns(2)

    col1.header("Dataframe")
    col1.write("Répartition des objets perdus par semaine :")
    col1.dataframe(objets_semaine, use_container_width=True)


    col2.header("Graphique")
    col2.write("Histrogramme des objets perdus par semaine de 2016 à 2021 :")
    col2.write(fig_semaine, use_column_width=True)

    ############ Question 2 : Afficher l’évolution du nombre d’objets perdus sur la période 2016-2021. ############
elif option == 'Question 2 : Afficher l’évolution du nombre d’objets perdus sur la période 2016-2021.':

    evolution = objets_perdus.reset_index().copy()
    evolution['date'] = evolution['date'].dt.strftime("%Y-%m")

    evolution.set_index('date', inplace=True)

    evolution = evolution.groupby(by=['type_objet', 'date']).count()

    del evolution['id_gare']
    del evolution['gare']


    left_col, right_col = st.columns(2)


    right_col.header("Dataframe")
    right_col.write("Évolution des objets perdus par type et par mois")
    right_col.dataframe(evolution, use_container_width=True)

    # left_col.header("LinePlot (Seaborn)")
    graph_type = left_col.selectbox('', ('Quels graphiques voulez-vous afficher?', 'Graphiques généraux', 'Graphique par année'), key="graph_type_selectbox")


    if graph_type == 'Graphiques généraux':

        fig2 = sns.lineplot(x='date', y='nature_objet', data=evolution)

        fig_type = fig2.get_figure()
        fig_type.set_size_inches(8, 5)

        ax = fig_type.gca()

        ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
        ax.tick_params(axis='x', labelsize=5)
        ax.set_ylabel("Nombre d'objets perdus par types")
        ax.set_xlabel("Mois de 2016 à 2021")

        col1, col2 = st.columns(2)


        col1.header("LinePlot (Seaborn)")
        col1.write("Évolution des objets perdus par type et par mois")
        col1.write(fig_type)



        fig3 = sns.scatterplot(x='date', y='nature_objet', data=evolution, hue="type_objet")

        fig_type_2 = fig3.get_figure()
        fig_type_2.set_size_inches(8, 7.35)

        ax = fig_type_2.gca()

        ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
        ax.tick_params(axis='x', labelsize=5)
        ax.set_ylabel("Évolution du nombre d'objets perdus")
        ax.set_xlabel("Mois de 2016 à 2021")
        ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

        col2.header("ScatterPlot (Seaborn)")
        col2.write("Répartition des objets perdus par type")
        col2.write(fig_type)
        col2.write("Sur ces deux graphiques, on peut visuellement observer que les pics d'objets perdus se trouvent principalement en été, on peut en déduire une hypothèse qui serait que peut-être les personnes perdent plus facilement leurs affaires au moment des vacances car elles sont beaucoup plus chargées. Les articles les plus souvent perdus sont les bagageries type sac et valise, ce qui tend à confimer l'hypothèse.")


        evolution2 = evolution.reset_index().copy()
        
        fig4 = px.line(evolution2, x='date', y='nature_objet',
                color='type_objet',
                title="Nombre d'objet perdu par type d'objet :")

        st.header("LinePlot (Plotly)")
        st.plotly_chart(fig4, use_container_width=True)

    elif graph_type == 'Graphique par année':
        graph_annee = left_col.selectbox('', ('Quelle année souhaitez-vous observer?', '2016', '2017', '2018', '2019', '2020', '2021'), key="graph_annee_selectbox")
        
        if graph_annee == 'Quelle année souhaitez-vous observer?':
            pass
        else:
            fig = px.line(objets_perdus.loc[f"{graph_annee}", "type_objet"].resample('M').count())
            st.plotly_chart(fig, use_container_width=True)
            if graph_annee == "2020":
                left_col.write("On peut voir une très forte baisse des objets perdus aux mois d'Avril et Mai de cet année. Cela se justifie par le confinement lié au COVID-19.")




    ############ Question 3 : Afficher une carte de France avec le nombre d’objets perdus en fonction de la fréquentation de voyageur de chaque région. ############
elif option == 'Question 3 : Afficher une carte de France avec le nombre d’objets perdus en fonction de la fréquentation de voyageur de chaque région.':
    france_map = folium.Map(location=[46.2276, 2.2137], zoom_start=6)
    conn = connector.connect(
    host="localhost",
    user="CodeBenji",
    password="Code!12345",
    database="sncf_meteo"
    )
    
    dataset = pd.read_sql("SELECT * FROM Frequentations", conn)

    def trouver_region(code_departement):
        departements_par_region = {
        "Nouvelle-Aquitaine": ["16", "17", "19", "23", "24", "33", "40", "47", "64", "79", "86", "87"],
        "Auvergne-Rhône-Alpes": ["01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"],
        "Bourgogne-Franche-Comté": ["21", "25", "39", "58", "70", "71", "89", "90"],
        "Bretagne": ["22", "29", "35", "56"],
        "Centre-Val de Loire": ["18", "28", "36", "37", "41", "45"],
        "Corse": ["2A", "2B"],
        "Grand Est": ["08", "10", "51", "52", "54", "55", "57", "67", "68", "88"],
        "Hauts-de-France": ["02", "59", "60", "62", "80"],
        "Île-de-France": ["75", "77", "78", "91", "92", "93", "94", "95"],
        "Normandie": ["14", "27", "50", "61", "76"],
        "Occitanie": ["11", "12", "30", "31", "32", "34", "46", "48", "65", "66", "81", "82"],
        "Pays de la Loire": ["44", "49", "53", "72", "85"],
        "Provence-Alpes-Côte d'Azur": ["04", "05", "06", "13", "83", "84"]
    }

        # On parcourt les régions et leurs départements
        for region, departements in departements_par_region.items():
            # Si le code de département se trouve dans la liste des départements de la région,
            # on renvoie la région
            if code_departement in departements:
                return region

    dataset["nom_regions"] = dataset["region"].apply(lambda x: trouver_region(x))
    months =['2016_01', '2016_02', '2016_03', '2016_04', '2016_05', '2016_06', '2016_07', '2016_08', '2016_09', '2016_10', '2016_11', '2016_12', '2017_01', '2017_02', '2017_03', '2017_04', '2017_05', '2017_06', '2017_07', '2017_08', '2017_09', '2017_10', '2017_11', '2017_12', '2018_01', '2018_02', '2018_03', '2018_04', '2018_05', '2018_06', '2018_07', '2018_08', '2018_09', '2018_10', '2018_11', '2018_12', '2019_01', '2019_02', '2019_03', '2019_04', '2019_05', '2019_06', '2019_07', '2019_08', '2019_09', '2019_10', '2019_11', '2019_12', '2020_01', '2020_02', '2020_03', '2020_04', '2020_05', '2020_06', '2020_07', '2020_08', '2020_09', '2020_10', '2020_11', '2020_12', '2021_01', '2021_02', '2021_03', '2021_04', '2021_05', '2021_06', '2021_07', '2021_08', '2021_09', '2021_10', '2021_11', '2021_12']
    selected_month = st.selectbox("Sélectionnez un mois", months)


    folium.Choropleth(
        columns=['nom_regions', selected_month],
        data=dataset,
        fill_color='BuPu',
        fill_opacity=1,
        key_on='feature.properties.nom',
        legend_name='frequence des voyageurs',
        line_opacity=0.5,
        geo_data='https://france-geojson.gregoiredavid.fr/repo/regions.geojson',
        highlight=True,
        name='frequentation',
        ).add_to(france_map)

    folium.LayerControl().add_to(france_map)
    sf.folium_static(france_map)





    ############ Question 4 : Afficher le nombre d’objets perdus en fonction de la température ############
elif option == 'Question 4 : Afficher le nombre d’objets perdus en fonction de la température':

    fig1 = px.scatter(objets_perdus2, x='temperature', y='nombre_objet',
            title="Nombre d'objets perdus en fonction de la température :"
    )



    st.header("Dataframe")
    st.write("Nombre d'objets perdus par mois et par région :")
    st.dataframe(objets_perdus2, use_container_width=True)

    col1, col2 = st.columns(2)

    col1.header("Graphique")
    col1.write(fig1)

    col2.header("Corrélation")
    col2.write("Affichage de la corrélation entre le nombre d'objets perdus et la température.")
    col2.dataframe(objets_perdus2.corr(), use_container_width=True)
    col2.write("Grâce au graphique et au calcul de corrélation de nos deux variables, on peut en déduire qu'il n'y pas de corrélation entre la température et le nombre d'objets perdus dans les trains.")


    ############ Question 5 et 6 : Quelle est la médiane du nombre d’objets perdus en fonction de la saison? Est ce que le nombre d’objets perdus est corrélé à la saison? ############
elif option == 'Question 5 et 6 : Quelle est la médiane du nombre d’objets perdus en fonction de la saison? Est ce que le nombre d’objets perdus est corrélé à la saison?':
    test_3_objets = objets_perdus3.set_index('date')
    test_3_objets = test_3_objets.resample('M').count().copy().reset_index()

    test_3_objets.drop(['id_gare', 'gare', 'type_objet', 'nature_objet'], axis=1, inplace=True)
    test_3_objets.rename(columns={"region":"nombre_objets"}, inplace=True)
    test_3_objets['date'] = test_3_objets['date'].dt.strftime("%Y_%0m")

    def mois(date = str):
        new_date = date[-2:]
        return new_date

    test_3_objets['saison'] = test_3_objets['date'].apply(lambda x : mois(str(x)))
    
    def saison(mois = str):
        printemps = ["03", "04", "05"]
        ete = ["06", "07", "08"]
        automne = ["09", "10", "11"]
        hiver = ["12", "01", "02"]

        if mois in printemps:
            return "printemps"
        elif mois in ete:
            return "ete"
        elif mois in automne:
            return "automne"
        elif mois in hiver:
            return "hiver"

    test_3_objets['saison'] = test_3_objets['saison'].apply(lambda x : saison(x))
    test_4_objets = test_3_objets.copy()

    fig_box = sns.boxplot(x='saison', y='nombre_objets', data=test_3_objets)
    fig_test_box = fig_box.get_figure()
    ax = fig_test_box.gca()
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    ax.tick_params(axis='x', labelsize=10)

    col_box1, col_box2 = st.columns(2)

    col_box1.title("Dataframe")
    col_box1.write("Affichage du nombre d'objets perdus par saison au niveau national.")
    col_box1.dataframe(test_3_objets, use_container_width=True)

    select_saison = col_box1.selectbox('Quelle médianne souhaitez-vous afficher?', ("Printemps", "Été", "Automne", "Hiver"))
    select_la_saison = select_saison.lower()
    select_la_saison = unicodedata.normalize("NFD", select_la_saison)
    select_la_saison = unicodedata.normalize("NFD", select_la_saison)
    select_la_saison = "".join([c for c in select_la_saison if not unicodedata.combining(c)])

    medians = test_3_objets.groupby('saison').median()
    median = medians['nombre_objets'][select_la_saison]
    median = round(median)

    col_box1.write(f'La médianne pour la saison "{select_saison}" est de {median} objets perdus pour la saison.')

    test_4_objets.reset_index(inplace=True)

    f_oneway_result = f_oneway(test_4_objets["nombre_objets"], test_4_objets['saison']=="hiver",test_4_objets['saison']=="printemps",test_4_objets['saison']=="ete",test_4_objets['saison']=="automne")
    
    col_box1.write(f'\nEn réalisant le test ANOVA sur nos données actuelles, on obtient les résultats suivants : \n - Statistiques : {f_oneway_result[0]}\n - p-value : {round(f_oneway_result[1],2)}')

    col_box2.title("Box-plot")
    col_box2.write("Les 4 Box-plots représentent la répartition des objets perdus en fonction des saisons.")
    col_box2.pyplot(fig_test_box)


    ############ Question 7 : Est ce que le type d’objets perdus est corrélé aux mois? ############
elif option == 'Question 7 : Est ce que le type d’objets perdus est corrélé aux mois?':
    test_5_objets = objets_perdus.reset_index().copy()
    test_5_objets['date'] = test_5_objets['date'].dt.month
    t5 = pd.crosstab(test_5_objets['type_objet'], test_5_objets['date'])
    chi2 = chi2_contingency(t5)

    st.header("Résultats du test Chi²")

    st.write("Nous souhaitons observer si le type des objets perdus est corrélé aux mois, c'est pourquoi nous réalisons un test statistique Chi² car nous devons comparer deux variables catégorielles entre elles.")

    st.write(f"La valeur du Chi² est de : {round(chi2[0], 2)}")

    st.write(f"La valeur de la p-value est de : {round(chi2[1], 4)}")

    st.write(f"La degré de liberté est de : {round(chi2[2], 2)}")
    st.write("")

    st.header("Table de contingence")
    st.write("Voici le dataframe reprenant la table de cotingence attendue sous l'hypothèse nulle. Cette table donne les valeurs attendues pour chaque combinaison de variables de la table de contingence, en utilisant les proportions de chaque valeur observée sur l'ensemble de la table.")

    st.dataframe(chi2[3], use_container_width=True)