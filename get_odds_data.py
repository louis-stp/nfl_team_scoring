from random import randint
import requests
import pandas as pd
import time

class Data_IO_Odds:

    def __init__(self):
        self.nameCodes = pd.read_csv('team_name_legend.csv',header=None)
        self.missingNames = set()

    #translates team names into team codes, for better consistency (franchises always have constant code)
    #and ease of url injection (url uses team codes not team names)
    def getTeamCode(self,namestring):
        code = "err"
        try: code = str(self.nameCodes[self.nameCodes[0]==namestring][1].values[0])
        except: self.missingNames.add(namestring)
        return code

    def processScore(self, scorestring):
        s = scorestring.replace('W ',"")
        s = s.replace('L ',"")
        s = s.replace('(OT)',"")
        s = s.replace(' ',"")
        s = s.replace('T',"")
        s = s.split("-")
        return s

    def processSpread(self, spreadstring):
        s = spreadstring.replace('W ',"")
        s = s.replace('L ',"")
        s = s.replace('P ',"")
        s = s.replace('PK',"0")
        return float(s)

    def processOverUnder(self, oustring):
        s = oustring.replace('O ',"")
        s = s.replace('U ',"")
        s = s.replace('P ',"")
        return float(s)

    def clean_df(self, df):
        df = df[df[0] != 'Notes']
        df = df[df[0] != 'Day']
        df = df.drop([0,1,2,3,7,10],axis=1)
        df['favorite'] = df[4].apply(self.getTeamCode)
        df['underdog'] = df[8].apply(self.getTeamCode)
        df['score'] = df[5].apply(self.processScore)
        df['f_points'] = df['score'].str[0].astype(float)
        df['u_points'] = df['score'].str[1].astype(float)
        df['spread'] = df[6].apply(self.processSpread)
        df['overunder'] = df[9].apply(self.processOverUnder)
        df = df.drop([4,5,6,8,9,'score'],axis=1)
        df = self.addDummyLabels(df)
        return df

    def addDummyLabels(self,df):
        df['spread_win'] = ((df['f_points']-df['u_points']) > -1*df['spread']).astype(int)
        df['spread_tie'] = ((df['f_points']-df['u_points']) == -1*df['spread']).astype(int)
        df['spread_loss'] = ((df['f_points']-df['u_points']) < -1*df['spread']).astype(int)
        df['ou_over'] = ((df['f_points']+df['u_points']) > df['overunder']).astype(int)
        df['ou_tie'] = ((df['f_points']+df['u_points']) == df['overunder']).astype(int)
        df['ou_under'] = ((df['f_points']+df['u_points']) < df['overunder']).astype(int)
        return df

    def loadOdds(self,years):
        df = pd.DataFrame()
        for year in years:
            print(year)
            url = 'https://www.sportsoddshistory.com/nfl-game-season/?y='+str(year)
            result = requests.get(url).text
            for i in range(6,23):
                tempdf = pd.read_html(result)[i]
                tempdf['week'] = i-5
                tempdf['season'] = year
                tempdf = dataio.clean_df(tempdf)
                df = pd.concat([df,tempdf],axis=0)
        print(self.missingNames)
        return df


dataio  = Data_IO_Odds()
df = dataio.loadOdds(range(2000,2022))
df.to_csv("game_odds")

