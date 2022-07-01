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
    mandat: 
    pd.read_csv(f"twitter_data/deputes_{mandat}_Twitter/deputes_{mandat}_Twitter_clean.csv")
    for mandat in ["2012", "2017", "2022"]
    }


# %%
def tokenize(text):
    """
    Tokenize text
    """
    tokens = nltk.word_tokenize(text)
    # remove punctuation
    tokens = [token.lower() for token in tokens if token.isalpha()]
    return [token.lower() for token in tokens]

def remove_stopwords(token):
    """
    Remove stopwords from text
    """
    stop_words = stopwords.words("french")
    stop_words += ["http", "https", "a"]
    return " ".join([word for word in token if word not in stop_words])

def clean_text(text):
    """
    Clean text
    """
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)
    text = unidecode.unidecode(tokens)
    return text

def count_frequency(text):
    """
    Count frequency of words in text
    """
    tokens = tokenize(text)
    return nltk.FreqDist(tokens)

# %%
for mandat in tqdm(df_deputes):
    df_deputes[mandat]["tweet_clean"] = df_deputes[mandat]["tweet"].map(clean_text)
    df_deputes[mandat]["tweet_frequency"] = df_deputes[mandat]["tweet_clean"].map(count_frequency)

dtale.show(df_deputes["2012"])


# %%
freq = {}
for mandat in tqdm(df_deputes):
    df_deputes[mandat].groupby(['parti'])['tweet_clean'].apply(','.join).reset_index()
    for parti in df_deputes[mandat]['parti']:
        # save value in variable
        text = df_deputes[mandat]['tweet_clean'][df_deputes[mandat]['parti'] == parti]
        freq[mandat] = Counter(text.split()).most_common()