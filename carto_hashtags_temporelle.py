# %% import modules
import pandas as pd
import json
import os
import dtale
from tqdm import tqdm
import plotly.express as px
import unidecode
import ast
import nltk
from nltk.corpus import stopwords
from collections import Counter

# %% load data
df_deputes = {
    mandat: pd.read_csv(
        f"twitter_data/deputes_{mandat}_Twitter/deputes_{mandat}_Twitter_clean.csv"
    )
    for mandat in ["2012", "2017", "2022"]
}


# %%
for mandat in df_deputes:
    df = df_deputes[mandat].copy()
    df["date"] = pd.to_datetime(df["date"])
    df["date"] = df["date"].dt.date
    df["hashtags"] = df["hashtags"].map(ast.literal_eval)
    df = df.explode("hashtags")

    hashtags_list = list(
        df.dropna(axis=0, subset="hashtags").query("hashtags != '[]'")["hashtags"]
    )

    df_timestamps = pd.DataFrame([], columns=["hashtags", "date", "type"])
    for hashtag in tqdm(set(hashtags_list)):
        df_hash = df.query(f"hashtags == '{hashtag}'")
        df_first = df_hash.sort_values("date").head(1)
        df_first["type"] = "first"
        df_last = df_hash.sort_values("date").tail(1)
        df_last["type"] = "last"
        df_timestamps = pd.concat(
            [
                df_timestamps,
                df_first[["hashtags", "date", "type"]],
                df_last[["hashtags", "date", "type"]],
            ]
        )

    df_timestamps.to_csv(
        f"twitter_data/deputes_{mandat}_Twitter/deputes_{mandat}_Twitter_timestamps.csv",
        index=False,
    )
    # dtale.show(df_timestamps).open_browser()


# %%
for mandat in df_deputes:
    df_timestamps = pd.read_csv(f"twitter_data/deputes_{mandat}_Twitter/deputes_{mandat}_Twitter_timestamps.csv")
    df_timestamps["hashtags"] = "#" + df_timestamps["hashtags"]
    df_start = df_timestamps.query("type == 'first'")
    df_end = df_timestamps.query("type == 'last'")
    
    start = dict(zip(df_start["hashtags"], df_start["date"]))
    end = dict(zip(df_end["hashtags"], df_end["date"]))

    df_nodes = pd.read_csv(f"twitter_data/deputes_{mandat}_Twitter/deputes_{mandat}_Twitter_hashtags_nodes.csv")
    df_nodes["start"] = df_nodes["label"].map(start)
    df_nodes["end"] = df_nodes["label"].map(end)
    df_nodes.to_csv(
        f"twitter_data/deputes_{mandat}_Twitter/deputes_{mandat}_Twitter_hashtags_nodes_timestamps.csv",
        index=False,
        )

        
# %%
