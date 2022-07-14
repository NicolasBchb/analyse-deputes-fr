# %% import modules
import pandas as pd
import plotly.express as px
import unidecode
import json
from math import log10

# %% load data
df_deputes = {
    mandat: pd.read_csv(f"data/{mandat}/data_deputes_{mandat}.csv")
    for mandat in ["2012", "2017", "2022"]
}


# %% prepare data
partis_merger = {
    "2022": {
        "Écologiste - Nupes": "NUPES",
        "Non inscrit": "Autres",
        "Rassemblement National": "RN",
        "Renaissance": "Ensemble",
        "La France insoumise - Nouvelle Union Populaire écologique et sociale": "NUPES",
        "Horizons et apparentés": "Ensemble",
        "Socialistes et apparentés (membre de l’intergroupe Nupes)": "NUPES",
        "Gauche démocrate et républicaine - Nupes": "NUPES",
        "Libertés, Indépendants, Outre-mer et Territoires": "Autres",
        "Les Républicains": "LR",
        "Démocrate (MoDem et Indépendants)": "Ensemble",
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
        "LR": "blue",
    },
    "2017": {
        "Autres": "grey",
        "UDI": "turquoise",
        "LREM": "orange",
        "LFI": "red",
        "PS": "HotPink",
        "LR": "blue",
    },
    "2012": {"Autres": "grey", "UMP": "blue", "PS": "HotPink", "UDI": "turquoise"},
}

for mandat in df_deputes:
    df_deputes[mandat]["etatCivil.infoNaissance.dateNais"] = pd.to_datetime(
        df_deputes[mandat]["etatCivil.infoNaissance.dateNais"]
    )
    df_deputes[mandat]["age"] = df_deputes[mandat][
        "etatCivil.infoNaissance.dateNais"
    ].apply(lambda x: (int(mandat) - x.year))

    df_deputes[mandat]["count"] = 1
    df_deputes[mandat]["sexe"] = 1
    df_deputes[mandat]["sexe"][
        df_deputes[mandat]["etatCivil.ident.civ"] == "Mme"
    ] = "Femmes"
    df_deputes[mandat]["sexe"][
        df_deputes[mandat]["etatCivil.ident.civ"] == "M."
    ] = "Hommes"

    df_deputes[mandat]["parti"] = df_deputes[mandat]["groupe"].map(
        partis_merger[mandat]
    )

    df_deputes[mandat]["nom"] = (
        df_deputes[mandat]["etatCivil.ident.nom"].map(
            lambda x: unidecode.unidecode(x).capitalize()
        )
        + " "
        + df_deputes[mandat]["etatCivil.ident.prenom"].map(
            lambda x: unidecode.unidecode(x).capitalize()
        )
    )


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
        marginal="box",  # can be `rug`, `violin`
    )
    ages.update_layout(
        title_text=f"<b>Histogramme des âges des députés ({mandat})</b>",
        margin=dict(l=0, r=0, t=70, b=40),
        plot_bgcolor="rgb(243, 243, 243)",
        bargap=0.2,
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
    marginal="box",  # can be `rug`, `violin`,
    color="annee_mandat",
    barmode="group",
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
    bargap=0.3,
)
ages.update_xaxes(title_text="<b><i>Âge</i></b>")
ages.update_yaxes(title_text="<b>Nombre de députés</b>")
ages.write_html("viz/ages_histo_global.html")


# %% professions (pas 2012)

for mandat in ["2017", "2022"]:

    fig = px.bar(
        df_deputes[mandat]
        .groupby(
            ["profession.socProcINSEE.catSocPro", "profession.socProcINSEE.famSocPro"]
        )
        .sum()
        .reset_index(),
        x="profession.socProcINSEE.famSocPro",
        y="count",
        color="profession.socProcINSEE.catSocPro",
        text="profession.socProcINSEE.catSocPro",
        log_y=True,
    )
    fig.update_layout(
        title_text=f"<b>Répartition des professions des députés ({mandat})</b>",
        margin=dict(l=0, r=0, t=70, b=40),
        plot_bgcolor="rgb(243, 243, 243)",
    )
    fig.update_xaxes(
        title_text="<b><i>Profession</i></b>", categoryorder="total descending"
    )
    fig.update_yaxes(title_text="<b>Nombre de députés</b>")

    fig.write_html(f"viz/professions_{mandat}.html")


# %% professions sun (pas 2012)

for mandat in ["2017", "2022"]:

    fig = px.sunburst(
        df_deputes[mandat]
        .groupby(
            ["profession.socProcINSEE.catSocPro", "profession.socProcINSEE.famSocPro"]
        )
        .sum()
        .reset_index()
        .sort_values(by="count", ascending=False),
        path=["profession.socProcINSEE.famSocPro", "profession.socProcINSEE.catSocPro"],
        values="count",
        color="profession.socProcINSEE.famSocPro",
        color_discrete_sequence=px.colors.qualitative.T10,
    )
    fig.update_layout(
        title_text=f"<b>Répartition des professions des députés ({mandat})</b>",
        margin=dict(l=0, r=0, t=70, b=40),
        plot_bgcolor="rgb(243, 243, 243)",
    )
    fig.update_traces(textinfo="label+percent parent", textfont=dict(size=16))
    fig.write_html(f"viz/professions_sun_{mandat}.html")

# %% professions (pas 2012)

for mandat in ["2017", "2022"]:

    fig = px.bar(
        df_deputes[mandat]
        .groupby(["profession.socProcINSEE.famSocPro"])
        .sum()
        .reset_index()
        .sort_values(by="count", ascending=False),
        x="profession.socProcINSEE.famSocPro",
        y="count",
        color="profession.socProcINSEE.famSocPro",
        color_discrete_sequence=px.colors.qualitative.Safe
        # log_y=True,
    )
    fig.update_layout(
        title_text=f"<b>Répartition des professions des députés ({mandat})</b>",
        margin=dict(l=0, r=0, t=70, b=40),
        plot_bgcolor="rgb(243, 243, 243)",
    )
    fig.update_xaxes(
        title_text="<b><i>Profession</i></b>", categoryorder="total descending"
    )
    fig.update_yaxes(title_text="<b>Nombre de députés</b>")
    fig.update_layout(showlegend=False)
    fig.write_html(f"viz/professions_bar_{mandat}.html")

# %% lieux de naissance
with open("carte\departements.json") as response:
    dep = json.load(response)

for mandat in df_deputes:

    df_temp = df_deputes[mandat].copy()
    df_temp = df_temp.groupby("etatCivil.infoNaissance.depNais").sum().reset_index()
    df_temp["logcount"] = df_temp["count"].map(lambda x: log10(x) * 100)

    dep_map = px.choropleth_mapbox(
        df_temp,
        geojson=dep,
        locations="etatCivil.infoNaissance.depNais",
        color="logcount",
        color_continuous_scale="OrRd",
        hover_data=["etatCivil.infoNaissance.depNais", "count"],
        range_color=(0, 160),
        mapbox_style="carto-positron",
        zoom=6,
        center={"lat": 47.081012, "lon": 2.398782},
        opacity=0.75,
        featureidkey="properties.nom",
    )

    dep_map.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        title_text=f"<b>Répartition des députés par département ({mandat})</b>",
        showlegend=False,
    )

    dep_map.write_html(f"viz/departements_map_{mandat}.html")

    fig_bar = px.bar(
        df_temp,
        x="etatCivil.infoNaissance.depNais",
        y="count",
        color="logcount",
        color_continuous_scale="OrRd",
        hover_data=["etatCivil.infoNaissance.depNais", "count"],
        range_color=(0, 160),
    )

    fig_bar.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        title_text=f"<b>Répartition des députés par département ({mandat})</b>",
        showlegend=False,
    )

    fig_bar.update_xaxes(
        title_text="<b><i>Département</i></b>", categoryorder="total descending"
    )

    fig_bar.update_yaxes(title_text="<b>Nombre de députés</b>")

    fig_bar.write_html(f"viz/departements_bar_{mandat}.html")

# %% ratio de députés en fonction de la population
pop_dep = pd.read_csv("data/Departements.csv", sep=";")
pop_dep_dict = dict(zip(pop_dep["DEP"], pop_dep["PTOT"]))

for mandat in df_deputes:

    df_temp = df_deputes[mandat].copy()
    df_temp = df_temp.groupby("etatCivil.infoNaissance.depNais").sum().reset_index()
    df_temp["logcount"] = df_temp["count"].map(lambda x: log10(x) * 100)
    df_temp["pop"] = df_temp["etatCivil.infoNaissance.depNais"].map(pop_dep_dict)
    df_temp["ratio"] = df_temp["pop"] / df_temp["count"]

    dep_map = px.choropleth_mapbox(
        df_temp,
        geojson=dep,
        locations="etatCivil.infoNaissance.depNais",
        color="ratio",
        color_continuous_scale="OrRd_r",
        hover_data=["etatCivil.infoNaissance.depNais", "ratio"],
        # range_color=(0, 160),
        mapbox_style="carto-positron",
        zoom=6,
        center={"lat": 47.081012, "lon": 2.398782},
        opacity=0.75,
        featureidkey="properties.nom",
    )

    dep_map.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        title_text=f"<b>Répartition des députés par département ({mandat})</b>",
        showlegend=False,
    )

    dep_map.write_html(f"viz/ratio_map_{mandat}.html")

    fig_bar = px.bar(
        df_temp,
        x="etatCivil.infoNaissance.depNais",
        y="ratio",
        color="ratio",
        color_continuous_scale="OrRd_r",
        hover_data=["etatCivil.infoNaissance.depNais", "ratio"],
        # range_color=(0, 160)
    )

    fig_bar.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        title_text=f"<b>Répartition des députés par département ({mandat})</b>",
        showlegend=False,
    )

    fig_bar.update_xaxes(
        title_text="<b><i>Département</i></b>", categoryorder="total ascending"
    )

    fig_bar.update_yaxes(title_text="<b>Nombre de députés</b>")

    fig_bar.write_html(f"viz/ratio_bar_{mandat}.html")


# %%
