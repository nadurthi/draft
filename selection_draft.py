# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
import gekko
import os
import random
import matplotlib.pyplot as plt
from gekko import GEKKO

df=pd.read_csv('/home/nadurthi/Downloads/draft-main/Preseries Player Stats - Copy - Static.csv')
df.reset_index(inplace=True)
df['cost'] = 100*(df['batting_score']+df['bowling_score']+df['allrounder_score']+df['fielding_score'])


# Batting optimization
N_batters=[3,7]
N_bowlers=[3,7]
N_keeper=[1,1]

batter_cost_range=[5000,500000]
bowler_cost_range=[5000,500000]
keeper_cost_range=[5000,500000]

max_batters_per_country =4
max_bowlers_per_country =4
max_keepers_per_country =1

max_cost = 500000
total_players = 11




qtiles = [.25, .5,.75,1]




# def generate_team(df):
df=df.copy()
countries = df['team'].unique()
# for c in countries:
#     df['is_'+c]=0
# for c in countries:    
#     for ind in df.index:
#         if df.loc[ind,'team']==c:
#             df.loc[ind,'is_'+c]=1
            
m = GEKKO()
for ind in df.index: 
    df.loc[ind,'vars'] = m.Var( lb=0, ub=1,integer=True, value=0,name=str(ind)) 


    

# batters --------------------------------
dfbat = df[df['is_batter']==True]
df_qtile = dfbat['cost'].quantile(qtiles)
Lind=[]
p=set([])
N_qts=[]
for qt in df_qtile:
    q = set( dfbat[dfbat['cost']<= qt].index)
    s=q-p
    Lind.append(s )
    N_qts.append(len(s))
    p = q
    
# pick 50% of players in each bucket
batter_ind_pick = [random.sample(list(Lind[i]),int(len(Lind[i])/2)) for i in range(len(Lind))] 
merge_batter_ind_pick=[]
for s in batter_ind_pick:
    merge_batter_ind_pick=merge_batter_ind_pick+s

# bowlers  -----------------  
dfbowl = df[df['is_bowler']==True]
df_qtile = dfbowl['cost'].quantile(qtiles)
Lind=[]
p=set([])
N_qts=[]
for qt in df_qtile:
    q = set( dfbowl[dfbowl['cost']<= qt].index)
    s=q-p
    Lind.append(s )
    N_qts.append(len(s))
    p = q
    
# pick 50% of players in each bucket
bowler_ind_pick = [random.sample(list(Lind[i]),int(len(Lind[i])/2)) for i in range(len(Lind))] 
merge_bowler_ind_pick=[]
for s in bowler_ind_pick:
    merge_bowler_ind_pick=merge_bowler_ind_pick+s
    
# keeper keeper--------------------------------------
dfkeeper = df[df['is_keeper']==True]
df_qtile = dfkeeper['cost'].quantile(qtiles)
Lind=[]
p=set([])
N_qts=[]
for qt in df_qtile:
    q = set( dfkeeper[dfkeeper['cost']<= qt].index)
    s=q-p
    Lind.append(s )
    N_qts.append(len(s))
    p = q
    
# pick 50% of players in each bucket
keeper_ind_pick = [random.sample(list(Lind[i]),int(len(Lind[i])/2)) for i in range(len(Lind))] 
merge_keeper_ind_pick=[]
for s in keeper_ind_pick:
    merge_keeper_ind_pick=merge_keeper_ind_pick+s

# all rounder  -----------
dfallround = df[df['is_all_rounder']==True]
df_qtile = dfallround['cost'].quantile(qtiles)
Lind=[]
p=set([])
N_qts=[]
for qt in df_qtile:
    q = set( dfallround[dfallround['cost']<= qt].index)
    s=q-p
    Lind.append(s )
    N_qts.append(len(s))
    p = q
    
# pick 50% of players in each bucket
allround_ind_pick = [random.sample(list(Lind[i]),int(len(Lind[i])/2)) for i in range(len(Lind))] 
merge_allround_ind_pick=[]
for s in allround_ind_pick:
    merge_allround_ind_pick=merge_allround_ind_pick+s

ind_picks =set.union(set(merge_batter_ind_pick),set(merge_bowler_ind_pick),set(merge_keeper_ind_pick),set(merge_allround_ind_pick))

dfpick = df.loc[list(ind_picks),:]
# dfpick=df.copy()


##  --------bulding cost


# batting cost
fbat=0
Nbat=0
bat_country={col:0 for col in countries}
for ind in dfpick[dfpick['is_batter']==True].index: 
    fbat =fbat+dfpick.loc[ind,'vars']*dfpick.loc[ind,'cost']
    Nbat =Nbat+dfpick.loc[ind,'vars']
    for col in countries:
        bat_country[col] = bat_country[col]+dfpick.loc[ind,'vars']*int(dfpick.loc[ind,'team']==col) 
    
    
m.Equation(fbat<=batter_cost_range[1])
m.Equation(fbat>=batter_cost_range[0])

m.Equation(Nbat<=N_batters[1])
m.Equation(Nbat>=N_batters[0])

for col in countries:
    m.Equation(bat_country[col]<=max_batters_per_country)
    

# bowling cost
fbwl=0
Nbwl=0
bowl_country={col:0 for col in countries}
for ind in dfpick[dfpick['is_bowler']==True].index: 
    fbwl =fbwl+dfpick.loc[ind,'vars']*dfpick.loc[ind,'cost']
    Nbwl =Nbwl+dfpick.loc[ind,'vars']
    for col in countries:
        bowl_country[col] = bowl_country[col]+dfpick.loc[ind,'vars']*int(dfpick.loc[ind,'team']==col) 
    
    
m.Equation(fbwl<=bowler_cost_range[1])
m.Equation(fbwl>=bowler_cost_range[0])

m.Equation(Nbwl<=N_bowlers[1])
m.Equation(Nbwl>=N_bowlers[0])

for col in countries:
    m.Equation(bowl_country[col]<=max_bowlers_per_country)
  

# keeper cost
fkeep=0
Nkeep=0
keeper_country={col:0 for col in countries}
for ind in dfpick[dfpick['is_keeper']==True].index: 
    fkeep =fkeep+dfpick.loc[ind,'vars']*dfpick.loc[ind,'cost']
    Nkeep =Nkeep+dfpick.loc[ind,'vars']
    for col in countries:
        keeper_country[col] = keeper_country[col]+dfpick.loc[ind,'vars']*int(dfpick.loc[ind,'team']==col) 
    
    
m.Equation(fkeep<=keeper_cost_range[1])
m.Equation(fkeep>=keeper_cost_range[0])

m.Equation(Nkeep<=N_keeper[1])
m.Equation(Nkeep>=N_keeper[0])

for col in countries:
    m.Equation(keeper_country[col]<=max_keepers_per_country)
  

# total players    
Nplayers=0
for ind in dfpick.index: 
    Nplayers =Nplayers+dfpick.loc[ind,'vars']
m.Equation(Nplayers==total_players)


# objective cost
totalcost=0
for ind in dfpick.index: 
    totalcost =totalcost+dfpick.loc[ind,'vars']*dfpick.loc[ind,'cost']

# m.Equation(totalcost<=max_cost)

    
m.Maximize(totalcost)

#Set global options
m.options.IMODE = 3 #steady state optimization

#Solve simulation
m.solve()

dfpick['vars_solve']= dfpick['vars'].apply(lambda x: int(x.value[0]))

dfpick[dfpick['vars_solve']==1][['team','name','is_batter','is_bowler','is_keeper','cost']]