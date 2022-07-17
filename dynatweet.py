#
# Attribution 4.0 International (CC BY 4.0) 
# 
import pandas as pd
import ast
import itertools
import csv
import collections
import codecs
import os
from tqdm import tqdm

years = ['2012','2017','2022']

for year in tqdm(years):
    out_path = f"dynatweet/{year}"
    os.makedirs(out_path, exist_ok=True)

    df = pd.read_csv(
            f"twitter_data/deputes_{year}_Twitter/deputes_{year}_Twitter_clean.csv"
        )

    """
        Pre process normalization
    """
    df["hashtags"] = df["hashtags"].map(ast.literal_eval) # Les hashtags comme une liste python (manipulable)
    df["date"] = pd.to_datetime(df["date"]).dt.strftime('%Y-%m-%dT%H:%M:%SZ') # date au format ISO 8061 (la base)
    
    """
        2 utilisations du dataset, pour générer la liste de nodes et la liste de liens.
        Du coup on copy
    """
    # On garde seulement les hashtags et la date
    df_nodes = df[['hashtags','date']].copy() 
    

    
    df_nodes = (df_nodes
                .explode("hashtags") # on "explose" la liste de hashtags pour créer un df hastag, date
                .dropna() # on retire les lignes vides / None 
                .groupby(by="hashtags")['date'] # on groupe part hashtag
                .apply(list) # quand on group, les dates récoltés on en fait une liste
                .str.join(', ') # La liste de date est transformé en une string "date1, date2, ..."
                .reset_index(name='timeset') # On va appeler cette colone 'timeset'
                ) 
    
    """
        Formatage node.csv "id, label, timeset"
    """
    df_nodes['timeset'] = df_nodes['timeset'].map('<[{}]>'.format) #  Format Timestamp set de gephi <[ts1,ts2, ...]>
    df_nodes['id'] = df_nodes['hashtags']
    df_nodes['label'] = df_nodes['hashtags']
    del df_nodes['hashtags']
    df_nodes.to_csv( f"{out_path}/Twitter_hashtags_nodes_timestamps.csv", index=False) # le dump


    # CSV a l'ancienne
    EDGES = collections.defaultdict(list) # On va stocker les liens ici
    df_edges = df[['hashtags','date']].copy()
    for idx, row in df_edges.iterrows():
        for h1,h2 in itertools.combinations(row['hashtags'],2): # Utilisez itertools, c'est cool pour faire des combinaisons / permutations 
            key = tuple(sorted((h1,h2))) # Technique legendraire pour identifier les liens sans direction :)
            EDGES[key].append(row['date']) # On ajoute la date

    # codecs parce que la france, le français et ces accents UTF-8        
    with codecs.open(f'{out_path}/Twitter_hashtags_edges_timestamps.csv', 'w', 'UTF-8') as csvfile:
        fieldnames = ['source', 'target','timeset'] # format edges.csv
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for (h1,h2),ts in EDGES.items():
                writer.writerow({'source': h1, 'target': h2, 'timeset':f"<[{', '.join(ts)}]>"}) # Même format pour timestamp set
        
            