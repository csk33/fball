# 2014-09-21
# this will pull game scores from espn
# these will be used to pull player box stats later
# christopher kim
#
# steps: 
# must have files games, games_old, and games_new initialized before kicking off these scripts

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date

path='C:\\Users\\Chris\\Desktop\\Fantasy\\Python\\'
year = 2014
teams = pd.read_csv(path+'teams.csv')
BASE_URL = 'http://espn.go.com/nba/team/schedule/_/name/{0}/year/{1}/seasontype/2/{2}'

match_id = []
dates = []
home_team = []
home_team_score = []
visit_team = []
visit_team_score = []

for index, row in teams.iterrows():
    _team, url = row['prefix_1'], row['url']
    r = requests.get(BASE_URL.format(row['prefix_1'], year, row['prefix_2']))
    table = BeautifulSoup(r.text).table
    for row in table.find_all('tr')[1:]: # Remove header
        columns = row.find_all('td')
        try:
            _home = True if columns[1].li.text == 'vs' else False
            _other_team = columns[1].find_all('a')[1]['href'].split('/')[-2]
            _score = columns[2].a.text.split(' ')[0].split('-')
            _won = True if columns[2].span.text == 'W' else False

            match_id.append(columns[2].a['href'].split('?id=')[1])
            home_team.append(_team if _home else _other_team)
            visit_team.append(_team if not _home else _other_team)
            d = datetime.strptime(columns[0].text, '%a, %b %d')
            if d.month > 6:
                year2 = year-1
            else:
                year2 = year

            dates.append(date(year2, d.month, d.day))

            if _home:
                if _won:
                    home_team_score.append(_score[0])
                    visit_team_score.append(_score[1])
                else:
                    home_team_score.append(_score[1])
                    visit_team_score.append(_score[0])
            else:
                if _won:
                    home_team_score.append(_score[1])
                    visit_team_score.append(_score[0])
                else:
                    home_team_score.append(_score[0])
                    visit_team_score.append(_score[1])
        except Exception as e:
            pass # Not all columns row are a match, is OK
            # print(e)

# fix the dates

dic = {'id': match_id, 'date': dates, 'home_team': home_team, 'visit_team': visit_team,
        'home_team_score': home_team_score, 'visit_team_score': visit_team_score}

games = pd.DataFrame(dic).drop_duplicates(cols='id').set_index('id')

#output list of games to file
games.to_csv(path+'games_'+str(year)+'.csv')

#read in last list of games and find the difference
games_old = pd.read_csv(path+'games_'+str(year)+'_old.csv').set_index('id')
games_new = pd.DataFrame(columns = games.columns)
for index,rows in games.iterrows():
    if index not in games_old.index:
        games_new = games_new.append(rows)

games_new.index.names = ['id']

#write this to a file
games_new.to_csv(path+'games_'+str(year)+'_new.csv')