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

df=pd.read_csv('G:\My Drive\Cricket\Preseries Player Stats - Copy - Static.csv')
df.reset_index(inplace=True)
df['cost'] = 100*(df['batting_score']+df['bowling_score']+df['allrounder_score']+df['fielding_score'])


# Batting optimization
N_batters=[1,5]
N_bowlers=[0,0]
N_keeper=[0,0]

batter_cost_range=[200000,5000000]
bowler_cost_range=[100000,500000]
keeper_cost_range=[100000,500000]

max_batters_per_country =7
max_bowlers_per_country =7
max_keepers_per_country =1

max_cost = 5000000

qtiles = [.25, .5,.75,1]

total_players = 3


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

# m.Equation(np.sum(bat_vars)>=N_batters[0])

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

m.Equation(totalcost<=max_cost)

    
m.Maximize(totalcost)

#Set global options
m.options.IMODE = 3 #steady state optimization

#Solve simulation
m.solve()

varsols = [int(v.value[0])==1 for v in df['vars']]
df_sol=[]
for ind in dfbat_opt.index:
    if dfbat_opt.loc[ind,'vars'].value[0]==1:
        df_sol.append({'type':'batter',
                'name':dfbat_opt.loc[ind,'name'],
                'country':dfbat_opt.loc[ind,'team'],
                'cost':dfbat_opt.loc[ind,'cost']})
for ind in dfbowl_opt.index:
    if dfbowl_opt.loc[ind,'vars'].value[0]==1:
        df_sol.append({'type':'bowler',
                       'name':dfbowl_opt.loc[ind,'name'],
                'country':dfbowl_opt.loc[ind,'team'],
                'cost':dfbowl_opt.loc[ind,'cost']})
for ind in dfkeeper_opt.index:
    if dfkeeper_opt.loc[ind,'vars'].value[0]==1:
        df_sol.append({'type':'keeper',
                       'name':dfkeeper_opt.loc[ind,'name'],
                'country':dfkeeper_opt.loc[ind,'team'],
                'cost':dfkeeper_opt.loc[ind,'cost']})        

df_sol = pd.DataFrame.from_records(df_sol)
df_sol
# return df_sol


