# %% import modules
import pandas as pd
import json
import os
import dtale
from tqdm import tqdm
import plotly.express as px
import unidecode
import ast

# %% load data
df_deputes = {}
for mandat in ["2012", "2017", "2022"]:
    with open(f"data/deputes_{mandat}.json") as f:
        df_deputes[mandat] = pd.json_normalize(json.load(f))

# %% Complete the 2022's dataframe
df_legislatives_2022 = pd.read_excel("data/resultats-legislatives-circos.xlsx")

df_legislatives_2022.rename(
    columns={
    "N°Panneau":"N°Panneau_0",
    "Sexe":"Sexe_0",
    "Nom":"Nom_0",
    "Prénom":"Prénom_0",
    "Nuance":"Nuance_0",
    "Voix":"Voix_0",
    "% Voix/Ins":"% Voix/Ins_0",
    "% Voix/Exp":"% Voix/Exp_0",
    "Sièges":"Sièges_0",
    "Unnamed: 28": "N°Panneau_1",
    "Unnamed: 29": "Sexe_1",
    "Unnamed: 30": "Nom_1",
    "Unnamed: 31": "Prénom_1",
    "Unnamed: 32": "Nuance_1",
    "Unnamed: 33": "Voix_1",
    "Unnamed: 34": "% Voix/Ins_1",
    "Unnamed: 35": "% Voix/Exp_1",
    "Unnamed: 36": "Sièges_1",
    "Unnamed: 37": "N°Panneau_2",
    "Unnamed: 38": "Sexe_2",
    "Unnamed: 39": "Nom_2",
    "Unnamed: 40": "Prénom_2",
    "Unnamed: 41": "Nuance_2",
    "Unnamed: 42": "Voix_2",
    "Unnamed: 43": "% Voix/Ins_2",
    "Unnamed: 44": "% Voix/Exp_2",
    "Unnamed: 45": "Sièges_2",
    }, 
    inplace=True
)

df_partis = pd.DataFrame([])
for i in range(3):
    df_it = df_legislatives_2022[[f"Nom_{i}", f"Nuance_{i}", f"Sièges_{i}"]]
    df_it.rename(columns={f"Nom_{i}": "nom_de_famille", f"Nuance_{i}": "nuance", f"Sièges_{i}": "sieges"}, inplace=True)
    df_it.dropna(subset=["sieges"], inplace=True)
    df_partis = df_partis.append(df_it, ignore_index=True)

df_partis.drop(columns=["sieges"], inplace=True)
df_partis["nom_de_famille"] = df_partis["nom_de_famille"].str.lower()
df_partis["nom_de_famille"] = df_partis["nom_de_famille"].str.replace("-", " ")
df_partis["nom_de_famille"] = df_partis["nom_de_famille"].apply(unidecode.unidecode)
df_deputes["2022"]["nom_de_famille"] = df_deputes["2022"]["nom_de_famille"].str.lower()
df_deputes["2022"]["nom_de_famille"] = df_deputes["2022"]["nom_de_famille"].str.replace("-", " ")
df_deputes["2022"]["nom_de_famille"] = df_deputes["2022"]["nom_de_famille"].apply(unidecode.unidecode)
# apply : if x endswith(' (de)'), x = "de " + x[:-5]
df_deputes["2022"]["nom_de_famille"][
    df_deputes["2022"]["nom_de_famille"].str.endswith(" (de)")
] = df_deputes["2022"]["nom_de_famille"][
    df_deputes["2022"]["nom_de_famille"].str.endswith(" (de)")
].map(lambda x: "de " + x[:-5])
df_deputes["2022"] = df_deputes["2022"].merge(df_partis, on="nom_de_famille", how="left")

premier_tour={
    "chikirou": "NUP",
    "corbiere": "NUP",
    "legrain": "NUP",
    "obono": "NUP",
    "favennec becot": "UDI",
}
for name in premier_tour:
    df_deputes["2022"].loc[df_deputes["2022"]["nom_de_famille"] == name, "nuance"] = premier_tour[name]


partis_sigles = {
    "NUP": "NUPES",
    "ENS": "Ensemble",
    "RN": "Rassemblement National",
    "LR": "Les Républicains",
    "DVG": "Divers Gauche",
    "DVD": "Divers Droite",
    "REG": "Régionalistes",
    "UDI": "Union des démocrates, radicaux et libéraux",
    "DVC": "Divers Centre",
    "DIV": "Divers",
    "DSV": "Droite souverainiste",
}

df_deputes["2022"]["parti_ratt_financier"] = df_deputes["2022"]["nuance"].map(partis_sigles)


# %% prepare data
partis_colors = {
    "2022": {
        "NUPES": "red",
        "Ensemble": "orange",
        "Rassemblement National": "SaddleBrown",
        "Les Républicains": "blue",
        # "Divers Gauche": "HotPink",
        # "Divers Droite": "RoyalBlue",
        # "Régionalistes": "DarkOliveGreen",
        "Autres": "grey",
    },
    "2017": {
        "Parti communiste français": "darkred",
        "Régions et peuples solidaires": "DarkOliveGreen",
        "La République en Marche": "orange",
        "Les Républicains": "blue",
        "Europe Écologie Les Verts": "green",
        "Parti socialiste": "HotPink",
        "Mouvement Démocrate": "OrangeRed",
        "Union des démocrates, radicaux et libéraux": "MediumPurple",
        "Rassemblement national": "SaddleBrown",
        "La France Insoumise": "red",
        "Autres": "grey",
    },
    "2012": {
        "Association PSLE - Nouveau centre": "orange",
        "Les Républicains": "blue",
        "Europe Écologie Les Verts": "green",
        "Parti socialiste": "HotPink",
        "Union des Radicaux, Indépendants et Démocrates": "MediumPurple",
        "Parti radical de gauche": "red",
        "Autres": "grey",
    },
}

elections ={
    "2012": {
        "presidentielles_1er":"2012-04-22 12:00:00",
        "presidentielles_2eme":"2012-05-06 12:00:00",
        "législatives_1er":"2012-06-10 12:00:00",
        "législatives_2eme":"2012-06-17 12:00:00",
    },
    "2017": {
        "presidentielles_1er":"2017-04-23 12:00:00",
        "presidentielles_2eme":"2017-05-07 12:00:00",
        "législatives_1er":"2017-06-11 12:00:00",
        "législatives_2eme":"2017-06-18 12:00:00",
    },
    "2022": {
        "presidentielles_1er":"2022-04-10 12:00:00",
        "presidentielles_2eme":"2022-04-24 12:00:00",
        "législatives_1er":"2022-06-12 12:00:00",
        "législatives_2eme":"2022-06-19 12:00:00",
    }
}

for mandat in df_deputes:
    df_deputes[mandat]["date_naissance"] = pd.to_datetime(
        df_deputes[mandat]["date_naissance"]
    )
    df_deputes[mandat]["age"] = df_deputes[mandat]["date_naissance"].apply(
        lambda x: (int(mandat) - x.year)
    )
    for column in df_deputes[mandat].columns:
        if column.startswith("twitter_data."):
            df_deputes[mandat].drop(column, axis=1, inplace=True)

    df_deputes[mandat]["parti_ratt_financier"][
        ~df_deputes[mandat]["parti_ratt_financier"].isin(partis_colors[mandat].keys())
    ] = "Autres"

    df_deputes[mandat]["count"] = 1
    df_deputes[mandat]["sexe"][df_deputes[mandat]["sexe"] == "F"] = "Femmes"
    df_deputes[mandat]["sexe"][df_deputes[mandat]["sexe"] == "H"] = "Hommes"


# %% Display data
for mandat in df_deputes:
    dtale.show(df_deputes[mandat]).open_browser()


# %% plot boxplot of age by party for each mandat (2012, 2017, 2022)
for mandat in df_deputes:
    ages_2017 = px.box(
        df_deputes[mandat],
        x="age",
        y="parti_ratt_financier",
        points="all",
        color="parti_ratt_financier",
        color_discrete_map=partis_colors[mandat],
        hover_name="nom",
    )
    ages_2017.update_layout(
        margin=dict(l=0, r=0, t=70, b=40),
        plot_bgcolor="rgb(243, 243, 243)",
        title_text=f"<b>Répartition de l'âge des députés par parti ({mandat})</b>",
    )
    ages_2017.update_traces(showlegend=False, line=dict(width=0.75))
    ages_2017.update_yaxes(
        title_text="<b>Parti politique</b>", categoryorder="median ascending"
    )
    ages_2017.update_xaxes(title_text="<b><i>Âge</i></b>")
    for data in ages_2017.data:
        data.marker.size = 2.5
    ages_2017.write_html(f"viz/ages_{mandat}.html")


# %% plot sunburst of parite by party for each mandat (2012, 2017, 2022)
for mandat in df_deputes:
    parite = px.sunburst(
        df_deputes[mandat],
        path=["parti_ratt_financier", "sexe"],
        values="count",
        color="parti_ratt_financier",
        color_discrete_map=partis_colors[mandat],
    )
    parite.update_layout(
        title_text=f"<b>Répartition des députés par parti et sexe ({mandat})</b>",
        margin=dict(l=0, r=0, t=70, b=40),
        plot_bgcolor="rgb(243, 243, 243)",
    )
    parite.update_traces(textinfo="label+percent parent", textfont=dict(size=16))
    parite.write_html(f"viz/parite_{mandat}.html")


# %% Sunburst à 3 étages pour 2017

df_deputes["2017"]["intergroupe"] = "Autres"

segmentation_2017 = {
    "Union des démocrates, radicaux et libéraux": "LR + UDI",
    "Les Républicains": "LR + UDI",
    "La République en Marche": "LREM + Modem",
    "Mouvement Démocrate": "LREM + Modem",
    "Parti socialiste": "Actuelle NUPES",
    "La France Insoumise": "Actuelle NUPES",
    "Europe Écologie Les Verts": "Actuelle NUPES",
    "Parti communiste français": "Actuelle NUPES",
    "Régions et peuples solidaires": "Autres",
    "Rassemblement national": "Autres", 
    "Autres": "Autres"
}

df_deputes["2017"]["intergroupe"] = df_deputes["2017"]["parti_ratt_financier"].map(
    segmentation_2017
)

parite = px.sunburst(
        df_deputes["2017"],
        path=["intergroupe", "parti_ratt_financier", "sexe"],
        values="count",
        # color="intergroupe",
        color_discrete_map={
            "LR + UDI": "blue",
            "LREM + Modem": "orange",
            "Actuelle NUPES": "red",
            "Autres": "grey",
        },
    )
parite.update_layout(
    title_text="<b>Répartition des députés par parti et sexe (2017)</b>",
    margin=dict(l=0, r=0, t=70, b=40),
    plot_bgcolor="rgb(243, 243, 243)",
)
parite.update_traces(textinfo="label+percent parent", textfont=dict(size=16))
parite.write_html("viz/parite_2017_intergroupes.html")
# %%
