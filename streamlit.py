import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import mysql.connector as connector
import plotly.express as px
import unicodedata

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


option = st.selectbox('', ('Quelle question voulez-vous afficher?', 'Question 1', 'Question 2', "Question 3 (en cours)", "Question 4", "Question 5 et 6", "Question 7 (en cours)"))


if option == 'Question 1':
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

    ############ Question 2 ############
elif option == 'Question 2':

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




    ############ Question 3 ############
elif option == 'Question 3':
    pass





    ############ Question 4 ############
elif option == 'Question 4':

    fig1 = px.scatter(objets_perdus2, x='temperature', y='nombre_objet',
            title="Nombre d'objets perdus en fonction de la température :"
    )



    st.header("Dataframe")
    st.write("Nombre d'objets perdus par mois et par région :")
    st.dataframe(objets_perdus2, use_container_width=True)

    col1, col2 = st.columns(2)

    col1.header("Graphique")
    col1.write(fig1, use_column_width=True)

    col2.header("Corrélation")
    col2.write("Affichage de la corrélation entre le nombre d'objets perdus et la température.")
    col2.dataframe(objets_perdus2.corr())
    col2.write("Grâce au graphique et au calcul de corrélation de nos deux variables, on peut en déduire qu'il n'y pas de corrélation entre la température et le nombre d'objets perdus dans les trains.")


    ############ Question 5 et 6 ############
elif option == 'Question 5 et 6':
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

    col_box2.title("Box-plot")
    col_box2.write("Les 4 Box-plots représentent la répartition des objets perdus en fonction des saisons.")
    col_box2.pyplot(fig_test_box)
