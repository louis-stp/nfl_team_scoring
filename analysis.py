from operator import pos
from unicodedata import name
from ortools.linear_solver import pywraplp
import numpy as np
import pandas as pd
import requests
import time


AVG_PTS_PER_GAME = 23

class Game:
    def __init__(self,team1, team2, t1points, t2points):
        self.team1 = team1
        self.team2 = team2
        self.t1points = t1points
        self.t2points = t2points

    def getTeams(self):
        return [self.team1, self.team2]
    
    def getPoints(self):
        return [self.t1points,self.t2points]


class Analysis:
    def __init__(self,teams,games):
        self.teams = teams
        self.games = games
    
    #this function uses integer programming to solve the match factor problem
    #Also calls functions at the end to format and display output
    def optimize(self):

        numConstraints = self.numConstraints()
        numVar = self.numVar()

        lp = pywraplp.Solver.CreateSolver('GLOP')
        infinity = lp.infinity()

        #creates variables
        x = {}
        for j in range(numVar):
            x[j] = lp.NumVar(0, infinity, 'x[%i]' % j)

        #define constraints
        slack_var_start_index = self.numTeams()*2
        defense_var_start_index = self.numTeams()
        slackvar_counter = 0
        for game in self.games:
            A_subset = np.zeros([4,numVar])
            B_subset = np.zeros(4)
            t1_index = self.teams.index(game.getTeams()[0])
            t2_index = self.teams.index(game.getTeams()[1])
            [t1_points,t2_points] = game.getPoints()

            for j in range(4):
                if j == 0:
                    A_subset[j,t1_index] = 1
                    A_subset[j,t2_index+defense_var_start_index] = -1
                    A_subset[j,slack_var_start_index+slackvar_counter] = -1
                    B_subset[j] = t1_points
                if j == 1:
                    A_subset[j,t1_index] = -1
                    A_subset[j,t2_index+defense_var_start_index] = 1
                    A_subset[j,slack_var_start_index+slackvar_counter] = -1
                    B_subset[j] = -t1_points
                if j == 2:
                    A_subset[j,t2_index] = 1
                    A_subset[j,t1_index+defense_var_start_index] = -1
                    A_subset[j,slack_var_start_index+slackvar_counter+1] = -1
                    B_subset[j] = t2_points
                if j == 3:
                    A_subset[j,t2_index] = -1
                    A_subset[j,t1_index+defense_var_start_index] = 1
                    A_subset[j,slack_var_start_index+slackvar_counter+1] = -1
                    B_subset[j] = -t2_points
                constraint = lp.RowConstraint(-infinity, B_subset[j], '')
                for k in range(numVar):
                    constraint.SetCoefficient(x[k], A_subset[j,k])
            slackvar_counter = slackvar_counter + 2
                
        C = np.zeros(numVar)
        for i in range(self.numTeams()*2,numVar):
            C[i] = 1

        #sets up objective function
        objective = lp.Objective()
        for j in range(numVar):
            objective.SetCoefficient(x[j], C[j])
        objective.SetMinimization()

        #solves IP problem
        status = lp.Solve()

        #Displays IP solver results. Useful for troubleshooting
        if status == pywraplp.Solver.OPTIMAL:
            for j in range(numVar):
                print(x[j].name(), ' = ', x[j].solution_value())
            print('Problem solved in %f milliseconds' % lp.wall_time())
            print('Problem solved in %d iterations' % lp.iterations())
            print('Objective value =', lp.Objective().Value())
        else:
            print('The problem does not have an optimal solution.')
        
        offense = []
        defense = []
        for i in range(self.numTeams()):
            offense += [x[i].solution_value()]
            defense += [x[i+self.numTeams()].solution_value()]

        return [self.teams, offense, defense]

    def numTeams(self):
        return len(self.teams)

    def numGames(self):
        return len(self.games)

    def numVar(self):
        return self.numTeams()*2 + self.numGames()*2

    def numConstraints(self):
        return self.numGames()*4

        
class DataIO:

    def __init__(self):
        pass

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
            df['season:Winner/tie'] = df['season'].astype(str) + ':' + df['Winner/tie']
            df['season:Loser/tie'] = df['season'].astype(str) + ':' + df['Loser/tie']
            df_master = pd.concat([df_master, df], ignore_index = True)
            #prevents overwhelming the website with requests
            time.sleep(.5)
        return df_master

    #returns a list of teams from the given year
    def getTeams(self, years):
        df = self.getGamesDF(years)
        winners = set(df['season:Winner/tie'].unique())
        losers = set(df['season:Loser/tie'].unique())
        return list(winners | losers)
        

    def getGames(self, years):
        df = self.getGamesDF(years)
        gameList = []
        for i in df.index:
            team1 = df.loc[i]['season:Winner/tie']
            team2 = df.loc[i]['season:Loser/tie']
            t1points = df.loc[i]['Pts']
            t2points = df.loc[i]['Pts.1']
            gameList += [Game(team1, team2, t1points, t2points)]
        return gameList

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

    #def getTeamVariables(self)

dataio = DataIO()
years = [2020, 2021]
obj = Analysis(dataio.getTeams(years), dataio.getGames(years))
[teams, offense, defense] = obj.optimize()