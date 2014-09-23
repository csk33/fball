# 2014-09-21
# this will create player summaries from the box scores
# christopher kim

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta

#set variables
path = 'C:\\Users\\Chris\\Desktop\\Fantasy\\Python\\'
year = 2014
time_period = {'all': 365, 'one_week': 7, 'two_weeks': 14, 'one_month': 31}
cols = ['MIN', 'FGM', 'FGA', 'FTM', 'FTA', '3PM', '3PA', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO']
cols_fnl = ['GP', 'MIN', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', '3PM', '3PA', '3P%', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO']
cols_val = ['MIN', 'FGA', 'FTA', '3PM', '3PA', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO']

#read box scores from csv and get game ids
full_box = pd.read_csv(path+'player_box_'+str(year)+'.csv').set_index('id')
games = pd.read_csv(path+'games_'+str(year)+'.csv').set_index('id')

#restrict dataset to only when player played and find different stats
no_dnp = full_box[full_box['MIN']>0]
no_dnp = no_dnp.join(games.date)
no_dnp['date'] = pd.to_datetime(no_dnp['date'])
#for i in range(0, len(no_dnp)):
#no_dnp.iloc[i, 22] = datetime.strptime(no_dnp.iloc[i, 22], '%Y-%m-%d')

#create datasets for each time_period
for key in time_period:
    time_delta = timedelta(-time_period[key])
    today = date.today()
    #today = date(2012, 11, 20)
    print key, time_delta
    
    interim_data = no_dnp[no_dnp['date'] >= today+time_delta]
    
    
    grouped = interim_data.groupby(interim_data['player'])
    #can try other way
    #function = ['count', 'sum', 'mean', 'std', 'median', 'max']
    #all_stats = grouped.agg(function)
    
    mean_stats = grouped.mean()
    count_stats = grouped.count()
    std_stats = grouped.std()
    
    #create dataframes for other stats (% stats, GP, etc)
    FGP = pd.DataFrame(mean_stats.FGM/mean_stats.FGA, index = mean_stats.index); FGP.columns = ['FG%']
    FTP = pd.DataFrame(mean_stats.FTM/mean_stats.FTA, index = mean_stats.index); FTP.columns = ['FT%']
    TPP = pd.DataFrame(mean_stats['3PM']/mean_stats['3PA'], index = mean_stats.index); TPP.columns = ['3P%']
    GP = pd.DataFrame(count_stats.MIN, index = count_stats.index); GP.columns = ['GP']
    
    total = pd.concat([GP, mean_stats[cols], FGP, FTP, TPP], axis = 1)
    total = total.fillna(0)
    total = np.round(total, 3)
    
    #order the columns as you want to see them
    total = total[cols_fnl]
    
    #stdev for consistency values
    std = pd.concat([GP, std_stats[cols_fnl_no_pct]], axis = 1)
    std = np.round(std, 3)
    
    #export to file
    total.to_csv(path+'player_stats_'+key+str(year)+'.csv')
    std.to_csv(path+'player_std_'+key+str(year)+'.csv')

#create league average stats
player_avg = pd.read_csv(path+'player_stats_all'+str(year)+'.csv').set_index('player')

#hard code 2014 NBA season values for top 13 rounds
nba14_avg = pd.Series([30.7654,14.4904,1.0706,3.4650, 5.5929,3.1128,1.0229,
                        0.6462,0.4658,11.5231,0.7762,3.4609,1.8763],
index = ['MIN', 'PTS', '3PM', '3PA', 'REB', 'AST', 'STL', 'BLK', 'FG%', 'FGA', 'FT%', 'FTA', 'TO'])
nba14_std = pd.Series([4.6356, 4.7905,0.8469,1.8936,2.6468,2.1650,0.4307, 
                        0.5586, 0.0492, 3.5908, 0.1046, 1.8472, 0.7522],
index = ['MIN', 'PTS', '3PM', '3PA', 'REB', 'AST', 'STL', 'BLK', 'FG%', 'FGA', 'FT%', 'FTA', 'TO'])

nba_totals = no_dnp[cols_fnl_no_pct].sum()
nba_avg = nba_totals/no_dnp.MIN.count()
nba_std = no_dnp[cols_fnl_no_pct].std()

# add FGV
#1 league avg %
#2 league avg FGA
#3 find diff between % and league %
#4 find % of FGA vs avg FGA
#5 3*4
#6 std of league 5
#7 divide 5 by 6


'''
#using hardcoded values
player_values = pd.DataFrame(columns = cols_fnl_no_pct)
for col in cols_val:
    if col == 'TO':
        player_values[col] = (nba14_avg[col] - player_avg[col])/nba14_std[col]
    else:
        player_values[col] = (player_avg[col] - nba14_avg[col])/nba14_std[col]


FG1 = player_avg['FG%']-nba14_avg['FG%']
FG2 = player_avg['FGA']/nba14_avg['FGA']
FG3 = FG1*FG2
FGV = pd.DataFrame(FG3/nba14_std['FG%'], index=player_avg.index); FGV.columns = ['FGV']

FT1 = player_avg['FT%']-nba14_avg['FT%']
FT2 = player_avg['FTA']/nba14_avg['FTA']
FT3 = FT1*FT2
FTV = pd.DataFrame(FT3/nba14_std['FT%'], index=player_avg.index); FTV.columns = ['FTV']

player_values2 = pd.concat([player_values, FGV, FTV], axis = 1)
player_values2['TOTAL'] = player_values2['FGV']+player_values2['FTV']+player_values2['3PM']+player_values2['PTS']+player_values2['REB']+player_values2['AST']+player_values2['STL']+player_values2['BLK']+player_values2['TO']
player_values_fin = player_values2[['TOTAL', 'FGV', 'FTV', '3PM', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO', 'MIN', '3PA', 'FGA', 'FTA']]
'''
#using real numbers
player_values = pd.DataFrame(columns = cols_fnl_no_pct)
for col in cols_val:
    if col == 'TO':
        player_values[col] = (nba_avg[col] - player_avg[col])/nba_std[col]
    else:
        player_values[col] = (player_avg[col] - nba_avg[col])/nba_std[col]

FG1 = player_avg['FG%']-float(nba_totals['FGM'])/nba_totals['FGA']
FG2 = player_avg['FGA']/nba_avg['FGA']
FG3 = FG1*FG2
nba_FGV_std = FG3.std()
FGV = pd.DataFrame(FG3/nba_FGV_std, index=player_avg.index); FGV.columns = ['FGV']

FT1 = player_avg['FT%']-float(nba_totals['FTM'])/nba_totals['FTA']
FT2 = player_avg['FTA']/nba_avg['FTA']
FT3 = FT1*FT2
nba_FTV_std = FT3.std()
FTV = pd.DataFrame(FT3/nba14_std['FT%'], index=player_avg.index); FTV.columns = ['FTV']

player_values2 = pd.concat([player_values, FGV, FTV], axis = 1)
player_values2['TOTAL'] = player_values2['FGV']+player_values2['FTV']+player_values2['3PM']+player_values2['PTS']+player_values2['REB']+player_values2['AST']+player_values2['STL']+player_values2['BLK']+player_values2['TO']
player_values_fin = player_values2[['TOTAL', 'FGV', 'FTV', '3PM', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO', 'MIN', '3PA', 'FGA', 'FTA']]

player_values_rnk = pd.DataFrame(player_values_fin.TOTAL.rank(ascending = False), index = player_values_fin.index)
player_values_rnk.columns = ['RNK']
player_values_fin2 = pd.concat([player_values_rnk, player_values_fin], axis = 1)
player_values_fin3 = player_values_fin2.sort(['RNK'], ascending = True)

player_values_fin3.to_csv(path+'player_values.csv')

#data cleanup -- remove outliers (top 3%, bottom 3% of stats)
#show likelihood calculations
#plot the player's stats on a graph
#keep track of players that are currently on peoples' teams
#calculate the general strength of all players in-use
#calculate the strength scores of all available players (value above average/replacement) overall and for each category
#optimize for weekly performance given the constraint of 2 adds per week
#optimize lineups for different matchups
#run regressions to see how much weight to give each variable 
#(involves finding strength of each category...finding the right weight to give 'consistency', etc)


#player_names = players2['player'].unique()

