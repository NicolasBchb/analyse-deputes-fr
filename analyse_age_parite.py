# %% import modules
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import unidecode
from tqdm import tqdm
import ast
import os
import json
import dtale

# %% load data
df_deputes = {
    mandat: pd.read_csv(f"data/{mandat}/data_deputes_{mandat}.csv")
    for mandat in ["2012", "2017", "2022"]
}


# %% prepare data
partis_merger = {
    "2022": {
        "Écologiste - Nupes":"NUPES",
        "Non inscrit":"Autres",
        "Rassemblement National":"RN",
        "Renaissance":"Ensemble",
        "La France insoumise - Nouvelle Union Populaire écologique et sociale":"NUPES",
        "Horizons et apparentés":"Ensemble",
        "Socialistes et apparentés (membre de l’intergroupe Nupes)":"NUPES",
        "Gauche démocrate et républicaine - Nupes":"NUPES",
        "Libertés, Indépendants, Outre-mer et Territoires":"Autres",
        "Les Républicains":"LR",
        "Démocrate (MoDem et Indépendants)":"Ensemble",
    },
    "2017": {
        "Écologie Démocratie Solidarité": "Autres",
        "UDI, Agir et Indépendants": "UDI",
        "Non inscrit": "Autres",
        "UDI et Indépendants": "UDI",
        "Gauche démocrate et républicaine": "Autres",
        "La République en Marche": "LREM",
        "La France insoumise": "LFI",
        "Socialistes et apparentés": "PS",
        "Libertés et Territoires": "Autres",
        "Agir ensemble": "UDI",
        "Nouvelle Gauche": "PS",
        "Les Constructifs : républicains, UDI, indépendants": "UDI",
        "Mouvement Démocrate (MoDem) et Démocrates apparentés": "LREM",
        "Les Républicains": "LR",
        "Mouvement Démocrate et apparentés": "LREM",
    },
    "2012": {
        "Écologiste": "Autres",
        "Non inscrit": "Autres",
        "Union pour un Mouvement Populaire": "UMP",
        "Socialiste, républicain et citoyen": "PS",
        "Gauche démocrate et républicaine": "Autres",
        "Radical, républicain, démocrate et progressiste": "PS",
        "Socialiste, écologiste et républicain": "PS",
        "Union des démocrates et indépendants": "UDI",
        "Les Républicains": "UMP",
    },
}

partis_colors = {
    "2022": {
        "NUPES": "red",
        "Autres": "grey",
        "RN": "SaddleBrown",
        "Ensemble": "orange",
        "LR": "blue"
    },
    "2017": {
        "Autres": "grey",
        "UDI": "turquoise",
        "LREM": "orange",
        "LFI": "red",
        "PS": "HotPink",
        "LR": "blue"
    },
    "2012": {
        "Autres": "grey",
        "UMP": "blue",
        "PS": "HotPink",
        "UDI": "turquoise"
    }
}

for mandat in df_deputes:
    df_deputes[mandat]["etatCivil.infoNaissance.dateNais"] = pd.to_datetime(
        df_deputes[mandat]["etatCivil.infoNaissance.dateNais"]
    )
    df_deputes[mandat]["age"] = df_deputes[mandat]["etatCivil.infoNaissance.dateNais"].apply(
        lambda x: (int(mandat) - x.year)
    )

    df_deputes[mandat]["count"] = 1
    df_deputes[mandat]["sexe"] = 1
    df_deputes[mandat]["sexe"][df_deputes[mandat]["etatCivil.ident.civ"] == "Mme"] = "Femmes"
    df_deputes[mandat]["sexe"][df_deputes[mandat]["etatCivil.ident.civ"] == "M."] = "Hommes"
        
    df_deputes[mandat]["parti"] = df_deputes[mandat]["groupe"].map(partis_merger[mandat])

    df_deputes[mandat]["nom"] = df_deputes[mandat]["etatCivil.ident.nom"].map(lambda x: unidecode.unidecode(x).capitalize()) + " " + df_deputes[mandat]["etatCivil.ident.prenom"].map(lambda x: unidecode.unidecode(x).capitalize())


# %% plot boxplot of age by party for each mandat (2012, 2017, 2022)
for mandat in df_deputes:
    ages_box = px.box(
        df_deputes[mandat],
        x="age",
        y="parti",
        points="all",
        color="parti",
        color_discrete_map=partis_colors[mandat],
        hover_name="nom",
    )
    ages_box.update_layout(
        margin=dict(l=0, r=0, t=70, b=40),
        plot_bgcolor="rgb(243, 243, 243)",
        title_text=f"<b>Répartition de l'âge des députés par parti ({mandat})</b>",
    )
    ages_box.update_traces(showlegend=False, line=dict(width=0.75))
    ages_box.update_yaxes(
        title_text="<b>Parti politique</b>", categoryorder="median ascending"
    )
    ages_box.update_xaxes(title_text="<b><i>Âge</i></b>")
    for data in ages_box.data:
        data.marker.size = 2.5
    ages_box.write_html(f"viz/ages_{mandat}.html")



# %% plot sunburst of parite by party for each mandat (2012, 2017, 2022)
for mandat in df_deputes:
    parite = px.sunburst(
        df_deputes[mandat],
        path=["parti", "sexe"],
        values="count",
        color="parti",
        color_discrete_map=partis_colors[mandat],
    )
    parite.update_layout(
        title_text=f"<b>Répartition des députés par parti et sexe ({mandat})</b>",
        margin=dict(l=0, r=0, t=70, b=40),
        plot_bgcolor="rgb(243, 243, 243)",
    )
    parite.update_traces(textinfo="label+percent parent", textfont=dict(size=16))
    parite.write_html(f"viz/parite_{mandat}.html")


# %%
for mandat in df_deputes:
    ages = px.histogram(
        df_deputes[mandat],
        x="age",
        y="count",
        nbins=df_deputes[mandat]["age"].nunique(),
        marginal="box", # can be `rug`, `violin`
    )
    ages.update_layout(
        title_text=f"<b>Histogramme des âges des députés ({mandat})</b>",
        margin=dict(l=0, r=0, t=70, b=40),
        plot_bgcolor="rgb(243, 243, 243)",
        bargap=0.2
    )
    ages.update_xaxes(title_text="<b><i>Âge</i></b>")
    ages.update_yaxes(title_text="<b>Nombre de députés</b>")
    ages.write_html(f"viz/ages_histo_{mandat}.html")

    
# %%
for mandat in df_deputes:
    df_deputes[mandat]["annee_mandat"] = mandat

df_global = pd.concat([df_deputes[mandat] for mandat in df_deputes])

ages = px.histogram(
    df_global,
    x="age",
    y="count",
    nbins=df_deputes[mandat]["age"].nunique(),
    marginal="box", # can be `rug`, `violin`,
    color="annee_mandat",
    barmode='group',
    color_discrete_sequence=px.colors.qualitative.Safe,
    color_discrete_map={
        "2012": "#F0244D",
        "2017": "#75B0F0",
        "2022": "#FC8C44",
    },
    opacity=0.7,
)

# ages.update_traces(line=dict(width=0.75))
ages.update_layout(
    title_text="<b>Répartition des âges des députés par mandat</b>",
    margin=dict(l=0, r=0, t=70, b=40),
    plot_bgcolor="rgb(243, 243, 243)",
    bargap=0.3
)
ages.update_xaxes(title_text="<b><i>Âge</i></b>")
ages.update_yaxes(title_text="<b>Nombre de députés</b>")
ages.write_html("viz/ages_histo_global.html")


# %% professions (pas 2012)



# %% lieux de naissance
