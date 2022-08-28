from random import randint
import requests
import pandas as pd
import time

AVG_PTS_PER_GAME = 23

class Data_IO:

    def __init__(self):
        self.nameCodes = pd.read_csv('team_name_legend.csv',header=None)

    #translates team names into team codes, for better consistency (franchises always have constant code)
    #and ease of url injection (url uses team codes not team names)
    def getTeamCode(self,namestring):
        code = str(self.nameCodes[self.nameCodes[0]==namestring][1].values[0])
        return code

    #since the dataframes always have the winner listed first, I randomly flip 50%
    #of the team and points values in their row order to prevent bias
    #so that the model does not "learn" that winners are always listed first
    def shuffleTeamOrder(self,df):
        df_shuffle = pd.DataFrame()
        for i in range(len(df.index)):
            row1 = {'season':[df.iloc[i]['season']],'OffenseTeam':[""],'DefenseTeam':[""],"pointsScored":[0]}
            row2 = {'season':[df.iloc[i]['season']],'OffenseTeam':[""],'DefenseTeam':[""],"pointsScored":[0]}
            row1['OffenseTeam'] = [self.getTeamCode(df.iloc[i]['Winner/tie'])]
            row1['DefenseTeam'] = [self.getTeamCode(df.iloc[i]['Loser/tie'])]
            row1['pointsScored'] = [df.iloc[i]['Pts']]

            row2['OffenseTeam'] = [self.getTeamCode(df.iloc[i]['Loser/tie'])]
            row2['DefenseTeam'] = [self.getTeamCode(df.iloc[i]['Winner/tie'])]
            row2['pointsScored'] = [df.iloc[i]['Pts.1']]

            #scrambles the order of which row is written first, thus not biasing
            #the order of labels
            if randint(0,1) == 1:
                temp_df1 = pd.DataFrame.from_dict(row1)
                temp_df2 = pd.DataFrame.from_dict(row2)
            else:
                temp_df1 = pd.DataFrame.from_dict(row2)
                temp_df2 = pd.DataFrame.from_dict(row1)
            df_shuffle = pd.concat([df_shuffle, temp_df1], ignore_index = True)
            df_shuffle = pd.concat([df_shuffle, temp_df2], ignore_index = True)
        return df_shuffle
            

    def getGamesDF(self, years):
        df_master = pd.DataFrame()
        for year in years:
            url = 'https://www.pro-football-reference.com/years/'+str(year)+'/games.htm'
            result = requests.get(url).text
            df = pd.read_html(result)[0]
            df = df[df['TOL'] != 'TOL']
            df = df.dropna(thresh=2)
            df = df.drop(labels=['Unnamed: 5','Unnamed: 7'], axis=1)
            df= df.astype({'Pts':int,'Pts.1':int,'YdsW':int,'TOW':int,'YdsL':int,'TOL':int})
            df['Pts'] = df['Pts'] - AVG_PTS_PER_GAME
            df['Pts.1'] = df['Pts.1'] - AVG_PTS_PER_GAME
            df['season'] = df['Date'].apply(self.getTeamSeason)
            df = df[['season','Winner/tie','Loser/tie','Pts','Pts.1']]
            df_master = pd.concat([df_master, df], ignore_index = True)
            #prevents overwhelming the website with requests
            time.sleep(.1)
        df_master = self.shuffleTeamOrder(df_master)
        return df_master

    #gets the appropriate season based on the year played, accounting for
    #wraparound (2022 superbowl is associated with 2021 season)
    def getTeamSeason(self, datestring):
      year = self.getYearFromDateString(datestring)
      if self.isEndOfSeason(datestring):
        year -= 1
      return year
    
    #takes the datestring pulled from the website and pulls out the year
    def getYearFromDateString(self, datestring):
      year = datestring[:4]
      year = int(year)
      assert (year > 1899 and year < 2100)
      return year

    #check if something is the end of season
    #This is important for labelling teams with the right season when games are
    #played in the following year (2021 team plays superbowl in early 2022)
    def isEndOfSeason(self, datestring):
      month = datestring[5:7]
      month = int(month)
      return month < 6

dataio = Data_IO()
gameData = dataio.getGamesDF(range(2010,2022))
gameData.to_csv('game_data')