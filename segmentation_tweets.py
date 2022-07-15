# %% import modules
import pandas as pd
import os
import dtale


# %% load data
df_tweets = {
    mandat: pd.read_csv(
        f"twitter_data/deputes_{mandat}_Twitter/deputes_{mandat}_Twitter_clean.csv"
    )
    for mandat in ["2012", "2017", "2022"]
}


df_comptes = {
    mandat: pd.read_csv(f"data/old/deputes_{mandat}.csv")
    for mandat in ["2012", "2017", "2022"]
}

for mandat in ["2012", "2017", "2022"]:
    df_comptes[mandat]["twitter"] = df_comptes[mandat]["twitter"].map(
        lambda x: x.lower()
    )


# %%
dicos_nuance = {
    mandat: dict(
        zip(df_comptes[mandat]["twitter"], df_comptes[mandat]["parti_ratt_financier"])
    )
    for mandat in ["2012", "2017", "2022"]
}

for mandat in df_tweets:
    df_tweets[mandat]["nuance"] = df_tweets[mandat]["username"].map(
        dicos_nuance[mandat]
    )

    df_tweets[mandat].to_csv(
        f"twitter_data/deputes_{mandat}_Twitter/deputes_{mandat}_Twitter_clean_nuance.csv",
        index=False,
    )


# %%
dtale.show(df_tweets["2017"]).open_browser()


# %%
for mandat in ["2012", "2017", "2022"]:
    os.makedirs(f"twitter_data/deputes_{mandat}_Twitter/nuances", exist_ok=True)
    for nuance in set(list(df_tweets[mandat]["nuance"])):
        df_nuance = df_tweets[mandat][df_tweets[mandat]["nuance"] == nuance]
        df_nuance.to_csv(
            f"twitter_data/deputes_{mandat}_Twitter/nuances/Twitter_{mandat}_{nuance}.csv",
            index=False,
        )


# %%
