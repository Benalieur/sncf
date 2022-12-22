import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import mysql.connector as connector
import plotly.express as px

############################# Récupération de la Database #############################

conn = connector.connect(
  host="localhost",
  user="CodeBenji",
  password="Code!12345",
  database="sncf_meteo"
)


objets_perdus = pd.read_sql("SELECT * FROM ObjetsPerdus", conn)



objets_perdus["date"] = pd.to_datetime(objets_perdus["date"])
objets_perdus.set_index("date", inplace=True)
objets_perdus.sort_index(inplace=True)

############################# Affichage Streamlit #############################

st.set_page_config(layout="wide",
    page_title="Objets Perdus SNCF")

st.title("Objets Perdus SNCF")


option = st.selectbox('', ('Quelle question voulez-vous afficher?', 'Question 1', 'Question 2'))


if option == 'Question 1':
    ############ Question 1 ############
    objets_semaine = objets_perdus.groupby(pd.Grouper(freq='W')).count()
    objets_semaine.drop(['id_gare', 'gare', 'nature_objet'], axis=1, inplace=True)
    objets_semaine.rename(columns={"type_objet":"Nombre Objets Perdus"},inplace=True)


    fig1 = sns.histplot(data=objets_semaine)
    fig_semaine = fig1.get_figure()
    fig_semaine.set_size_inches(8, 4)


    col1, col2 = st.columns(2)

    col1.header("Tableau")
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


    left_col.header("Dataframe")
    left_col.write("Évolution des objets perdus par type et par mois")
    left_col.dataframe(evolution, use_container_width=True)

    right_col.header("LinePlot (Seaborn)")
    graph_type = right_col.selectbox('', ('Quels graphiques voulez-vous afficher?', 'Graphiques généraux', 'Graphique par année'))


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
        
        fig4 = px.scatter(evolution2, x='date', y='nature_objet',
                color='type_objet',
                title="Nombre d'objet perdu par type d'objet :")

        st.header("ScatterPlot (Plotly)")
        st.plotly_chart(fig4, theme="streamlit", use_container_width=True)

    elif graph_type == 'Graphique par année':
        graph_annee = right_col.selectbox('', ('Quels graphiques voulez-vous afficher?', 'Graphiques généraux', 'Graphique par année'))
        if graph_annee == 'Graphique par année':
            st.write(objets_perdus.loc["2017", "type_objet"].resample('M').count().plot())
