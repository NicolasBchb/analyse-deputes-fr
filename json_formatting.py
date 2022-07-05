# %% import libraries
import json
import os
from tqdm import tqdm
import pandas as pd
import dtale

# %% merge and clean 2022/2017 data
for annee in ["2017", "2022"]:
    acteurs = []
    for file in tqdm(os.listdir(f"data/{annee}/json/acteur")):
        if file.endswith(".json"):
            with open(f"data/{annee}/json/acteur/{file}", "r") as f:
                data = json.load(f)
                data = data["acteur"]
            if type(data["mandats"]["mandat"]) == list:
                mandat_list = data["mandats"]["mandat"]
            else:
                mandat_list = [data["mandats"]["mandat"]]

            if any(mandat["typeOrgane"] == "ASSEMBLEE" for mandat in mandat_list):
                gp = [mandat["organes"]["organeRef"] for mandat in mandat_list if mandat["typeOrgane"] == "GP"]
                data_clean = {
                    "etatCivil": data["etatCivil"], 
                    "profession": data["profession"], 
                    "mandat_assemblée": [mandat for mandat in mandat_list if mandat["typeOrgane"] == "ASSEMBLEE"][0], 
                    "GP": gp[0] if gp else "None"
                    }

                acteurs.append(data_clean)


    organes = []
    for file in tqdm(os.listdir(f"data/{annee}/json/organe")):
        if file.endswith(".json"):
            with open(f"data/{annee}/json/organe/{file}", "r") as f:
                data = json.load(f)
                data = data["organe"]
                if data["codeType"] == "GP":
                    organes.append(data)


    json_complet = {"acteurs": acteurs, "organes": organes}
    with open(f"data/{annee}/data_deputes_{annee}.json", "w") as f:
        json.dump(json_complet, f)


# %% clean 2012 data
with open("data/2012/data_deputes_2012_old.json", "r") as f:
    data = json.load(f)

acteurs_clean = []
for acteur in tqdm(data["acteurs"]):
    if type(acteur["mandats"]["mandat"]) == list:
        mandat_list = acteur["mandats"]["mandat"]
    else:
        mandat_list = [acteur["mandats"]["mandat"]]

    if any(mandat["typeOrgane"] == "ASSEMBLEE" for mandat in mandat_list):
        gp = [mandat["organes"]["organeRef"] for mandat in mandat_list if mandat["typeOrgane"] == "GP"]
        data_clean = {
            "etatCivil": acteur["etatCivil"], 
            # "profession": acteur["profession"], 
            "mandat_assemblée": [mandat for mandat in mandat_list if mandat["typeOrgane"] == "ASSEMBLEE"][0], 
            "GP": gp[0] if gp else "None"
            }

        acteurs_clean.append(data_clean)

organes_clean = [organe for organe in tqdm(data["organes"]) if organe["codeType"] == "GP"]

data_clean = {"acteurs": acteurs_clean, "organes": organes_clean}

with open("data/2012/data_deputes_2012.json", "w") as f:
    json.dump(data_clean, f)

    
# %%
for annee in ["2012", "2017", "2022"]:
    with open(f"data/{annee}/data_deputes_{annee}.json", "r") as f:
        data = json.load(f)
    df = pd.json_normalize(data["acteurs"])
    gp = {organe["uid"] : organe["libelle"] for organe in data["organes"]}
    if annee == "2017":
        df = df[df["mandat_assemblée.legislature"] == "15"]
    gp["None"] = "Non inscrit"
    df["groupe"] = df["GP"].map(gp)
    df.to_csv(f"data/{annee}/data_deputes_{annee}.csv", index=False)



# %%
