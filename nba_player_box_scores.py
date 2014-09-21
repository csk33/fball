# 2014-09-21
# this will pull player box scores from espn
# christopher kim

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date

year=2013
games = pd.read_csv('C:\\Users\\Chris\\Desktop\\games_'+str(year)+'_new.csv').set_index('id')
BASE_URL = 'http://espn.go.com/nba/boxscore?gameId={0}'

request = requests.get(BASE_URL.format(games.index[0]))

table = BeautifulSoup(request.text).find('table', class_='mod-data')
heads = table.find_all('thead')
headers = heads[0].find_all('tr')[1].find_all('th')[1:]
headers = [th.text for th in headers]
columns = ['id', 'team', 'player'] + headers

players = pd.DataFrame(columns=columns)

def get_players(players, team_name):
    array = np.zeros((len(players), len(headers)+1), dtype=object)
    array[:] = np.nan
    for i, player in enumerate(players):
        cols = player.find_all('td')
        array[i, 0] = cols[0].text.split(',')[0]
        for j in range(1, len(headers) + 1):
            if not cols[1].text.startswith('DNP'):
                if j in (1, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14):
                    array[i,j] = int(cols[j].text)
                else:
                    array[i, j] = cols[j].text
            else:
                if j in (1, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14):
                    array[i,j] = 0
                else:
                    array[i, j] = str('0-0')  
    frame = pd.DataFrame(columns=columns)

    for x in array:
        line = np.concatenate(([index, team_name], x)).reshape(1,len(columns))
        new = pd.DataFrame(line, columns=frame.columns)
        frame = frame.append(new)
    return frame

for index, row in games.iterrows():
    print(index)
    request = requests.get(BASE_URL.format(index))
    table = BeautifulSoup(request.text).find('table', class_='mod-data')
    heads = table.find_all('thead')
    bodies = table.find_all('tbody')
    
    team_1 = heads[0].th.text
    team_1_players = bodies[0].find_all('tr') + bodies[1].find_all('tr')
    team_1_players = get_players(team_1_players, team_1)
    players = players.append(team_1_players)
    
    team_2 = heads[3].th.text
    team_2_players = bodies[3].find_all('tr') + bodies[4].find_all('tr')
    team_2_players = get_players(team_2_players, team_2)
    players = players.append(team_2_players)

players2 = players.set_index('id')

#split out FG, FT, and 3P
FGM = players2['FGM-A'].str.split('-').str[0]
for i in range(0,len(FGM)):
    FGM[i] = int(FGM[i])

players2['FGM'] = pd.Series(FGM, index=players2.index)

FGA = players2['FGM-A'].str.split('-').str[1]
for i in range(0,len(FGA)):
    FGA[i] = int(FGA[i])

players2['FGA'] = pd.Series(FGA, index=players2.index)
#players2['FGA'] = pd.Series(players2['FGM-A'].str.split('-').str[1], index=players2.index)

FTM = players2['FTM-A'].str.split('-').str[0]
for i in range(0,len(FTM)):
    FTM[i] = int(FTM[i])

players2['FTM'] = pd.Series(FTM, index=players2.index)

FTA = players2['FTM-A'].str.split('-').str[1]
for i in range(0,len(FTA)):
    FTA[i] = int(FTA[i])

players2['FTA'] = pd.Series(FTA, index=players2.index)

TPM = players2['3PM-A'].str.split('-').str[0]
for i in range(0,len(TPM)):
    TPM[i] = int(TPM[i])

players2['3PM'] = pd.Series(TPM, index=players2.index)

TPA = players2['3PM-A'].str.split('-').str[1]
for i in range(0,len(FGA)):
    TPM[i] = int(TPA[i])

players2['3PA'] = pd.Series(TPA, index=players2.index)


#fix the dataframe types to take stats
columns=players2.columns
for i in columns:
    if i in ('MIN', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PF', '+/-', 'PTS', 'FGM', 'FGA', 'FTM', 'FTA', '3PM', '3PA'):
        players2[i] = players2[i].convert_objects(convert_numeric=True)

#players2.to_csv('C:\\Users\\Chris\\Desktop\\player_box_'+str(year)+'.csv')
# to append
players2.to_csv('C:\\Users\\Chris\\Desktop\\player_box_'+str(year)+'.csv', mode='a', header=False)

#set the latest list of games for which we've pulled data as the 'old' games file to compare to next time
games_all = pd.read_csv('C:\\Users\\Chris\\Desktop\\games_'+str(year)+'.csv').set_index('id')
games_all.to_csv('C:\\Users\\Chris\\Desktop\\games_'+str(year)+'_old.csv')

