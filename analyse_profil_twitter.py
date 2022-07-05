# %% import modules
import pandas as pd
import json
import dtale
import plotly.express as px
import plotly.graph_objects as go
import unidecode
from tqdm import tqdm
import ast
import os

# %% load data
df_deputes = {}
for mandat in ["2012", "2017", "2022"]:
    with open(f"data/deputes_{mandat}.json") as f:
        df_deputes[mandat] = pd.json_normalize(json.load(f))

# %% Complete the 2022's dataframe
df_legislatives_2022 = pd.read_excel("data/resultats-legislatives-circos.xlsx")

df_legislatives_2022.rename(
    columns={
        "N°Panneau": "N°Panneau_0",
        "Sexe": "Sexe_0",
        "Nom": "Nom_0",
        "Prénom": "Prénom_0",
        "Nuance": "Nuance_0",
        "Voix": "Voix_0",
        "% Voix/Ins": "% Voix/Ins_0",
        "% Voix/Exp": "% Voix/Exp_0",
        "Sièges": "Sièges_0",
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
    inplace=True,
)

df_partis = pd.DataFrame([])
for i in range(3):
    df_it = df_legislatives_2022[[f"Nom_{i}", f"Nuance_{i}", f"Sièges_{i}"]]
    df_it.rename(
        columns={
            f"Nom_{i}": "nom_de_famille",
            f"Nuance_{i}": "nuance",
            f"Sièges_{i}": "sieges",
        },
        inplace=True,
    )
    df_it.dropna(subset=["sieges"], inplace=True)
    df_partis = df_partis.append(df_it, ignore_index=True)

df_partis.drop(columns=["sieges"], inplace=True)
df_partis["nom_de_famille"] = df_partis["nom_de_famille"].str.lower()
df_partis["nom_de_famille"] = df_partis["nom_de_famille"].str.replace("-", " ")
df_partis["nom_de_famille"] = df_partis["nom_de_famille"].apply(unidecode.unidecode)
df_deputes["2022"]["nom_de_famille"] = df_deputes["2022"]["nom_de_famille"].str.lower()
df_deputes["2022"]["nom_de_famille"] = df_deputes["2022"]["nom_de_famille"].str.replace(
    "-", " "
)
df_deputes["2022"]["nom_de_famille"] = df_deputes["2022"]["nom_de_famille"].apply(
    unidecode.unidecode
)
df_deputes["2022"]["nom_de_famille"][
    df_deputes["2022"]["nom_de_famille"].str.endswith(" (de)")
] = df_deputes["2022"]["nom_de_famille"][
    df_deputes["2022"]["nom_de_famille"].str.endswith(" (de)")
].map(
    lambda x: "de " + x[:-5]
)
df_deputes["2022"] = df_deputes["2022"].merge(
    df_partis, on="nom_de_famille", how="left"
)

premier_tour = {
    "chikirou": "NUP",
    "corbiere": "NUP",
    "legrain": "NUP",
    "obono": "NUP",
    "favennec becot": "UDI",
}
for name in premier_tour:
    df_deputes["2022"].loc[
        df_deputes["2022"]["nom_de_famille"] == name, "nuance"
    ] = premier_tour[name]


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

df_deputes["2022"]["parti_ratt_financier"] = df_deputes["2022"]["nuance"].map(
    partis_sigles
)


# %% prepare data
partis_colors = {
    "2022": {
        "NUPES": "red",
        "Ensemble": "orange",
        "Rassemblement National": "SaddleBrown",
        "Les Républicains": "blue",
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


for mandat in df_deputes:
    for column in df_deputes[mandat].columns:
        if column.startswith("twitter_data."):
            df_deputes[mandat].drop(column, axis=1, inplace=True)

    df_deputes[mandat]["parti_ratt_financier"][
        ~df_deputes[mandat]["parti_ratt_financier"].isin(partis_colors[mandat].keys())
    ] = "Autres"


# %%
influenceurs = {}
for mandat in df_deputes:
    influenceurs[mandat] = px.histogram(
        df_deputes[mandat].sort_values("twitter_followers", ascending=False).head(30),
        x="twitter_name",
        y="twitter_followers",
        title=f"Influenceurs députés de {mandat}",
        log_y=True,
        color="parti_ratt_financier",
        color_discrete_map=partis_colors[mandat],
        opacity=0.66,
    )

    influenceurs[mandat].update_xaxes(
        title_text="<b><i>Nom</i></b>", categoryorder="total descending"
    )
    influenceurs[mandat].update_yaxes(title_text="<b>Nombre de followers</b>")

    influenceurs[mandat].write_html(
        f"twitter_data/deputes_{mandat}_Twitter/influenceurs_{mandat}.html"
    )


# %%
accros = {}
for mandat in df_deputes:
    accros[mandat] = px.histogram(
        df_deputes[mandat].sort_values("twitter_tweets", ascending=False).head(30),
        x="twitter_name",
        y="twitter_tweets",
        title=f"Députés accros à Twitter de {mandat}",
        # log_y=True,
        color="parti_ratt_financier",
        color_discrete_map=partis_colors[mandat],
        opacity=0.66,
    )

    accros[mandat].update_xaxes(
        title_text="<b><i>Nom</i></b>", categoryorder="total descending"
    )
    accros[mandat].update_yaxes(title_text="<b>Nombre de tweets</b>")

    accros[mandat].write_html(
        f"twitter_data/deputes_{mandat}_Twitter/accros_{mandat}.html"
    )


# %%
influenceurs_go = {}
accros_go = {}
for mandat in df_deputes:
    df = df_deputes[mandat].sort_values("twitter_followers", ascending=False).head(10)
    x = df["twitter_name"]
    y = df["twitter_followers"]
    z = df["parti_ratt_financier"]
    influenceurs_go[mandat] = go.Bar(
        x=x,
        y=y,
        marker_color=list(map(lambda x: partis_colors[mandat][x], z)),
        opacity=0.66,
    )

    df = df_deputes[mandat].sort_values("twitter_tweets", ascending=False).head(10)
    x = df["twitter_name"]
    y = df["twitter_tweets"]
    z = df["parti_ratt_financier"]
    accros_go[mandat] = go.Bar(
        x=x,
        y=y,
        marker_color=list(map(lambda x: partis_colors[mandat][x], z)),
        opacity=0.66,
    )


# %%
from plotly.subplots import make_subplots

fig = make_subplots(
    rows=3,
    cols=2,  # vertical_spacing=0.5,
    subplot_titles=(
        "<i>Députés influenceurs 2022</i>",
        "<i>Députés les plus actifs du 1er janv. au 1er juin 2022</i>",
        "<i>Députés influenceurs 2017</i>",
        "<i>Députés les plus actifs du 1er janv. au 1er juin 2017</i>",
        "<i>Députés influenceurs 2012</i>",
        "<i>Députés les plus actifs du 1er janv. au 1er juin 2012</i>",
    ),
)

fig.add_trace(influenceurs_go["2022"], row=1, col=1)

fig.add_trace(accros_go["2022"], row=1, col=2)

fig.add_trace(influenceurs_go["2017"], row=2, col=1)

fig.add_trace(accros_go["2017"], row=2, col=2)

fig.add_trace(influenceurs_go["2012"], row=3, col=1)

fig.add_trace(accros_go["2012"], row=3, col=2)

fig.update_layout(
    margin=dict(l=60, r=30, t=120, b=30),
    plot_bgcolor="rgb(243, 243, 243)",
    bargap=0.3,
    title="<b><i>Les députés et Twitter (2012, 2017, 2022)</i></b>",
    title_x=0.5,
    showlegend=False,
    font_size=10,
)

fig.update_annotations(font_size=12)

for i, mandat in enumerate(df_deputes):
    i += 1
    fig.update_yaxes(title_text="<b>Nombre de followers</b>", type="log", row=i, col=1)
    fig.update_yaxes(title_text="<b>Nombre de tweets</b>", side="right", row=i, col=2)

fig.update_xaxes(
    title_text="<b><i>Nom</i></b>", row=3, col=1, categoryorder="total descending"
)
fig.update_xaxes(
    title_text="<b><i>Nom</i></b>", row=3, col=2, categoryorder="total descending"
)

fig.write_html("subplot_twitter.html")

# %%
