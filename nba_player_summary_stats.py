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
year = 2013
time_period = {'all': 365, 'one_week': 7, 'two_weeks': 14, 'one_month': 31}
cols = ['MIN', 'FGM', 'FGA', 'FTM', 'FTA', '3PM', '3PA', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO']
cols_fnl = ['GP', 'MIN', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', '3PM', '3PA', '3P%', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO']
cols_fnl_no_pct = ['MIN', 'FGM', 'FGA', 'FTM', 'FTA', '3PM', '3PA', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO']

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
    #today = date.today()
    today = date(2012, 11, 20)
    print key, time_delta
    
    interim_data = no_dnp[no_dnp['date'] >= today+time_delta]
    
    
    
    grouped = interim_data.groupby(interim_data['player'])
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

