from distutils.command.build import build
import pandas as pd
import numpy as np
import os
import random
from tqdm import tqdm
mydir = 'E:/repos/nfl_team_scoring/simplified'
myfile = 'game_data.csv'

AVG_PTS_PER_GAME = 23

game_data = pd.read_csv(os.path.join(mydir, myfile)).drop('Unnamed: 0', axis=1)
game_data = game_data.replace('WildCard',19)
game_data = game_data.replace('Division',20)
game_data = game_data.replace('Conference',21)
game_data = game_data.replace('ConfChamp',21)
game_data = game_data.replace('SuperBowl',22)

#ticks down one week in the game schedule
def tickDown(season, week):
    week = int(week)
    if week >= 2:
        week = week-1
        return [season, week]
    else:
        week = 18
        season = season - 1
        return [season, week]

#returns relevant info from most recent game before the provided inputs
def getPreviousGame(season, week, teamCode):
    failed_searches = 0
    found_prev = False
    prev_game = {'season':0, 'week':0, 'team':teamCode,'opponent':'xxx', 'pointsFor':0,'pointsAgainst':0, 'won?':0, 'missingData?':1}

    while failed_searches <= 2:
        [season, week] = tickDown(season, week)
        row_query = game_data[(game_data['season']==season) & (game_data['Week']==str(week)) & ((game_data['Team1']==teamCode) | (game_data['Team2']==teamCode))]
        #checks if it found a game where the give team played
        if len(row_query) < 1:
            #if it failed more than twice, give up
            failed_searches = failed_searches + 1
            continue
        #if it found a game, reset fail counter and pull the index
        else:
            failed_searches = 0
            prev_game['season'] = season
            prev_game['week'] = week
            prev_game['missingData?'] = False
            if row_query.Team2.values[0] == teamCode:
                prev_game['opponent'] = row_query.Team1.values[0]
                prev_game['pointsFor'] = row_query.pts2.values[0]
                prev_game['pointsAgainst'] = row_query.pts1.values[0]
                prev_game['won?'] = (prev_game['pointsFor'] > prev_game['pointsAgainst'])
            elif row_query.Team1.values[0] == teamCode:
                prev_game['opponent'] = row_query.Team2.values[0]
                prev_game['pointsFor'] = row_query.pts1.values[0]
                prev_game['pointsAgainst'] = row_query.pts2.values[0]
                prev_game['won?'] = (prev_game['pointsFor'] > prev_game['pointsAgainst'])
            else:
                raise ValueError('Teamcode not found in the query row') 
            break
    return prev_game

#builds a full row of data based on historical game performance
def buildRow_half(season, week, teamCode):
    numFirstOrders = 20
    numSecondOrders = 0
    numThirdOrders = 0
    firstOrderResults = []
    secondOrderResults = []
    thirdOrderResults = []

    prev = []
    i = 0
    while i < numFirstOrders:
        if i == 0:
            prev = getPreviousGame(season, week, teamCode)
        else:
            prev = getPreviousGame(prev['season'],prev['week'],prev['team'])
        firstOrderResults += [prev]
        i = i + 1

    for entry in firstOrderResults:
        i = 0
        prev = entry
        while i < numSecondOrders:
            if i == 0:
                prev = getPreviousGame(prev['season'],prev['week'],prev['opponent'])
            else:
                prev = getPreviousGame(prev['season'],prev['week'],prev['team'])
            secondOrderResults += [prev]
            i = i + 1

    for entry in secondOrderResults:
        i = 0
        prev = entry
        while i < numThirdOrders:
            if i == 0:
                prev = getPreviousGame(prev['season'],prev['week'],prev['opponent'])
            else:
                prev = getPreviousGame(prev['season'],prev['week'],prev['team'])
            thirdOrderResults += [prev]
            i = i + 1

    row = []
    for entry in firstOrderResults:
        row += [entry['pointsFor']]
        row += [entry['pointsAgainst']]
        #row += [int(entry['season'] != season)]
        #row += [int(entry['won?'])]
        #row += [int(entry['missingData?'])]
    
    for entry in secondOrderResults:
        row += [entry['pointsFor']]
        row += [entry['pointsAgainst']]
        #row += [int(entry['season'] != season)]
        #row += [int(entry['won?'])]
        #row += [int(entry['missingData?'])]

    for entry in thirdOrderResults:
        row += [entry['pointsFor']]
        row += [entry['pointsAgainst']]
        #row += [int(entry['season'] != season)]
        #row += [int(entry['missingData?'])]
    
    return(row)

#combines the half rows for each team into a full data row
def buildFullRow(season, week, team1, team2):
    #the order the team comes in is biased, so there is a 50% chance the teams are
    half1 = buildRow_half(season, week, team1)
    half2 = buildRow_half(season, week, team2)

    #builds the row from the parts
    #addes the team strings to to first 2 rows
    fullRow = [team1, team2]
    fullRow += half1
    fullRow += half2

    return fullRow

#stitches together the full dataset and labels to input into the model
def buildDataSet():
    X = []
    y = []
    
    for i,row in tqdm(game_data.iterrows()):
        if i < 100:
            continue

        team1 = row.Team1
        team2 = row.Team2
        team1_pts = row.pts1 + AVG_PTS_PER_GAME
        team2_pts = row.pts2 + AVG_PTS_PER_GAME
        
        data_row = buildFullRow(row.season, row.Week, team1, team2)
        label_row = [team1_pts, team2_pts]

        X += [data_row]
        y += [label_row]

    return [X,y]


[X, y] = buildDataSet()
dfX = pd.DataFrame(X)
dfy = pd.DataFrame(y, columns=['team1_pts','team2_pts'])
dfX.to_csv('nfl_team_scoring/simplified/X_data_20_0_0.csv', index=False)
dfy.to_csv('nfl_team_scoring/simplified/y_data_20_0_0.csv',index=False)
