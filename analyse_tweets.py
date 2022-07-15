# %% import modules
import pandas as pd
from tqdm import tqdm
import plotly.express as px
from nltk import RegexpTokenizer
from nltk.corpus import stopwords
from french_lefff_lemmatizer.french_lefff_lemmatizer import FrenchLefffLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from unidecode import unidecode
import re
import os

# %% def ngram
lemmatizer = FrenchLefffLemmatizer()
tokener = RegexpTokenizer(r"\w+")

with open("data/stopwords_fr.txt", "r") as f:
    sw = f.read().splitlines()

sw = [unidecode(mot) for mot in sw]

def clean_stopwords_ngram(token):
    clean = [
        lemmatizer.lemmatize(x, "v") for x in token if (x not in sw and not x.isdigit())
    ]
    phrase = ""
    for mot in clean:
        phrase = phrase + " " + mot
    return phrase


def ngram(sentences, n=3, top=30, firstword=""):
    c = CountVectorizer(ngram_range=(n, n))
    X = c.fit_transform(sentences)
    words = (
        pd.DataFrame(X.sum(axis=0), columns=c.get_feature_names())
        .T.sort_values(0, ascending=False)
        .reset_index()
    )
    return words[words["index"].apply(lambda x: firstword in x)].head(top)


def ngram_tweets(df, dossier, nom_export, n=3, top=100):
    df["tweet"] = df["tweet"].map(unidecode)
    df["tweet"] = df["tweet"].map(lambda x: re.sub("(@[A-Za-z]+[A-Za-z0-9-_]+)", "", x))
    df["tweet"] = df["tweet"].map(lambda x: re.sub(r"http\S+", "", x))
    df["tweet"] = df["tweet"].str.lower()
    df["tweet"] = df["tweet"].map(tokener.tokenize)
    df["tweet"] = df["tweet"].map(clean_stopwords_ngram)

    gram = ngram(df.tweet, n, top)
    gram.columns = ["ngram", "count"]

    fig = px.bar(gram, x="ngram", y="count")

    if n == 1:
        pre = "mono"
    elif n == 2:
        pre = "bi"
    elif n == 3:
        pre = "tri"
    else:
        pre = str(n)

    chemin_xlsx = os.path.join(dossier, nom_export + "_" + pre + "gram.xlsx")
    gram.to_excel(chemin_xlsx, engine="openpyxl")
    chemin_html = os.path.join(dossier, nom_export + "_" + pre + "gram.html")
    fig.write_html(chemin_html)

    return fig


# %%

for mandat in ["2012", "2017", "2022"]:
    for nuance in os.listdir(f"twitter_data/deputes_{mandat}_Twitter/nuances"):
        if nuance.endswith(".csv"):
            df = pd.read_csv(
                f"twitter_data/deputes_{mandat}_Twitter/nuances/{nuance}"
            )
            for n in [1, 2, 3]:
                ngram_tweets(df, f"twitter_data/deputes_{mandat}_Twitter/nuances", f"{nuance}_{mandat}", n)


# %%

