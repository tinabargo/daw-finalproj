#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask, jsonify, send_from_directory
import pandas as pd
import fim
import numpy as np
from ast import literal_eval


# In[2]:


app = Flask(__name__, static_folder='web')

# Load dataset of pokemon teams
df = pd.read_csv('./data/df_top25.csv')
# Convert 'Team' from string to list of strings
df['Team List'] = df['Team'].apply(lambda x: literal_eval(x))
# Load dataset of best PH players
df2 = pd.read_csv('./data/phchallengers.csv')
m, n = df2.shape
# Load Pokemon Types 
df_types = pd.read_csv('./data/poketype.csv')
df_types['Pokemon Type/s'] = df_types['Pokemon Type/s'].apply(lambda x: literal_eval(x))
df_types['Strong Against'] = df_types['Strong Against'].apply(lambda x: literal_eval(x))
df_types['Weak Against'] = df_types['Weak Against'].apply(lambda x: literal_eval(x))

ptypelist = ['Normal', 'Fighting', 'Flying', 'Poison', 'Ground', 'Rock', 
'Bug', 'Ghost', 'Steel', 'Fire', 'Water', 'Grass', 'Electric', 'Psychic',
'Ice', 'Dragon', 'Fairy', 'Dark']


# ---

# In[3]:


""" @app.route('/<string:path>')
def get_static(path):
    print(path)
    return send_from_directory('./web', path) """


# In[4]:


# Return list of available tournaments
@app.route('/list/tourneys')
def get_tourneylist():
    tourneylist = list(set(df['Tournament']))
    # Remove the special tournaments (no global theme)
    tourneylist.remove('Season 1 Championship')
    tourneylist.remove('Season 1 Group Stage')
    tourneylist.remove('Season 1 Regionals')
    tourneylist.remove('Ranked Tournament')
    tourneylist.remove('Open Great League (Ranked) Tournament')
    
    return jsonify(tourneylist)


# In[5]:


# Return list of all pokemon types
@app.route('/list/pokemon-types')
def get_ptypelist():
    return jsonify(ptypelist)


# In[6]:


# Return results PokeType Filter
@app.route('/pokedata/<string:poketype>')
def get_typelists(poketype):
    
    # Filter Pokemon List to only return the type selected
    df_poketype = df_types.copy()
    df_poketype['is_in'] = df_poketype['Pokemon Type/s'].apply(lambda x: poketype in x)   
    df_poketype = df_poketype[df_poketype['is_in']==True]
    
    # Create dictionary for output
    dict_results = {}
    dict_results['pokeid'] = list(df_poketype['Pokemon ID'])
    dict_results['pokemon'] = list(df_poketype['Pokemon Name'])
    dict_results['types'] = list(df_poketype['Pokemon Type/s'])
    dict_results['strong'] = list(df_poketype['Strong Against'])
    dict_results['weak'] = list(df_poketype['Weak Against'])

    return jsonify(dict_results)


# In[7]:


# Return results of FIM on tourneycup
@app.route('/data/<string:tourneycup>')
def get_fim(tourneycup):
    # Select specific tournament from dataset
    df_tourney = df[df['Tournament']==tourneycup]
    db_tourney = list(df_tourney['Team List'])

    # FIM using FP-Growth
    tuplelist = sorted(fim.fpgrowth(db_tourney, supp=1, report='S'), key=lambda x:-x[1])
    tuplelist = list(map(lambda x: (list(x[0]), x[1]), tuplelist))
    fim_tourney = pd.DataFrame(tuplelist, columns=['team', 'relsup'])
    cutoff = fim_tourney.loc[4,'relsup']
    top_tourney = fim_tourney[fim_tourney['relsup']>=cutoff]

    # Create dictionary for output
    dict_results = {}
    dict_results['teamlist'] = list(top_tourney['team'])
    dict_results['rsuplist'] = list(top_tourney['relsup'])

    return jsonify(dict_results)


# In[8]:


# Return dictionary of player stats
@app.route('/data/players')
def get_playerstats():
    # Create dictionary for output
    dict_pinfo = {}
    p_rank = [str(x) for x in np.arange(1,m+1)]
    dict_pinfo['player_rank'] = p_rank
    dict_pinfo['player_id'] = list(df2['Player ID'])
    dict_pinfo['player_url'] = list(df2['Player URL'])
    dict_pinfo['nbattles'] = list(df2['Battles'].astype(str))
    dict_pinfo['nwins'] = list(df2['Wins'].astype(str))
    dict_pinfo['nlosses'] = list(df2['Losses'].astype(str))

    return jsonify(dict_pinfo)

if __name__ == '__main__':
    app.run()

