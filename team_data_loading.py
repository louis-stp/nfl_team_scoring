import pandas as pd
import requests
import time

class PlayerDataIO:

  def getRbVars(self,df_offense):
    df = df_offense.droplevel(0,axis=1)
    df = df[(df['Pos'] == 'RB') | (df['Pos'] == 'rb')]
    df = df.sort_values(by=['GS'], ascending = False)
    df = df.reset_index(drop=True)[:2]
    returnList = [df['Y/A'][0],df['A/G'][0],df['Y/A'][1],df['A/G'][1]]
    return returnList

  def getWrVars(self,df_offense):
    df = df_offense.droplevel(0,axis=1)
    df = df[(df['Pos'] == 'WR') | (df['Pos'] == 'wr')]
    df = df.sort_values(by=['GS'], ascending = False)
    df = df.reset_index(drop=True)[:2]
    returnList = [df['Y/Tgt'][0],float(df['Ctch%'][0][:-1]),df['R/G'][0],df['Y/Tgt'][1],float(df['Ctch%'][1][:-1]),df['R/G'][1]]
    return returnList

  def getQbVars(self,df_passing):
    df = df_passing.copy()
    df = df[(df['Pos'] == 'QB') | (df['Pos'] == 'qb')]
    df = df.sort_values(by=['GS'], ascending = False)
    df = df.reset_index(drop=True)[:1]
    returnList = [float(str(df['Cmp%'][0])[:-1]),float(str(df['Int%'][0])[:-1]),df['Y/A'][0],df['Y/G'][0]]
    return returnList

  def getTeVars(self,df_offense):
    df = df_offense.droplevel(0,axis=1)
    df = df[(df['Pos'] == 'TE') | (df['Pos'] == 'te')]
    df = df.sort_values(by=['GS'], ascending = False)
    df = df.reset_index(drop=True)[:1]
    df = df[['Player','Y/Tch','Ctch%','YScm']]
    returnList = [df['Y/Tch'][0],float(df['Ctch%'][0][:-1]),df['Y/Tch'][0]]
    return returnList

  def getOlVars(self,df_passing):
    df = df_passing.copy()
    df = df[(df['Pos'] == 'QB') | (df['Pos'] == 'qb')]
    df = df.sort_values(by=['GS'], ascending = False)
    df = df.reset_index(drop=True)[:1]
    returnList = [float(str(df['Sk%'][0])[:-1])]
    return returnList

  def getKcVars(self,df_kicking):
    df = df_kicking.copy()
    df = df.sort_values(by=[('Scoring','FGA')], ascending = False)
    df = df.reset_index(drop=True)[:1]
    fg_b40 = (float(df['20-29']['FGA']) + float(df['30-39']['FGA'])) / (float(df['20-29']['FGM']) + float(df['30-39']['FGM']))
    fg_a40 = (float(df['40-49']['FGA']) + float(df['50+']['FGA'])) / (float(df['40-49']['FGM']) + float(df['50+']['FGM']))
    fgp = float(str(df['Scoring']['FG%'][0])[:-1])
    return [fg_b40,fg_a40,fgp]


  def getOffenseVars(self, df_offense,df_passing,df_kicking):
    rbVars = self.getRbVars(df_offense)
    wrVars = self.getWrVars(df_offense)
    qbVars = self.getQbVars(df_passing)
    teVars = self.getTeVars(df_offense)
    olVars = self.getOlVars(df_passing)
    kcVars = self.getKcVars(df_kicking)
    return[*qbVars,*wrVars,*rbVars,*teVars,*olVars,*kcVars]

  def getDeVars(self,df_defense):
    df = df_defense.copy()
    df = df[(df['Unnamed: 3_level_0']['Pos'].str.contains('DE') == True) | (df['Unnamed: 3_level_0']['Pos'].str.contains('de') == True)]
    df = df.sort_values(by=[('Games','GS')], ascending=False)
    df = df.reset_index(drop=True)[:2]
    df['TFL/GS'] = df['Tackles']['TFL'].astype(float)/df['Games']['GS'].astype(float)
    df['QBH/GS'] = df['Tackles']['QBHits'].astype(float)/df['Games']['GS'].astype(float)
    returnList = [df['TFL/GS'][0],df['QBH/GS'][0],df['TFL/GS'][1],df['QBH/GS'][1]]
    return returnList
    
  def getDtVars(self,df_defense):
    df = df_defense.copy()
    df = df[(df['Unnamed: 3_level_0']['Pos'].str.contains('DT') == True) | (df['Unnamed: 3_level_0']['Pos'].str.contains('dt') == True)]
    df = df.sort_values(by=[('Games','GS')], ascending=False)
    df = df.reset_index(drop=True)[:1]
    df['COMB/GS'] = df['Tackles']['Comb'].astype(float)/df['Games']['GS'].astype(float)
    df['TFL/GS'] = df['Tackles']['TFL'].astype(float)/df['Games']['GS'].astype(float)
    df['QBH/GS'] = df['Tackles']['QBHits'].astype(float)/df['Games']['GS'].astype(float)
    try:
      returnList = [df['COMB/GS'][0],df['TFL/GS'][0],df['QBH/GS'][0]]
    except:
      returnList = [0,0,0]
    return returnList

  def getSVars(self,df_defense):
    df = df_defense.copy()
    df = df[(df['Unnamed: 3_level_0']['Pos'].str.contains('S') == True) | (df['Unnamed: 3_level_0']['Pos'].str.contains('s') == True)]
    df = df.sort_values(by=[('Games','GS')], ascending=False)
    df = df.reset_index(drop=True)[:2]
    df['PD/GS'] = df['Def Interceptions']['PD'].astype(float)/df['Games']['GS'].astype(float)
    df['COMB/GS'] = df['Tackles']['Comb'].astype(float)/df['Games']['GS'].astype(float)
    returnList = [df['PD/GS'][0],df['COMB/GS'][0],df['PD/GS'][1],df['COMB/GS'][1]]
    return returnList

  def getCbVars(self,df_defense):
    df = df_defense.copy()
    df = df[(df['Unnamed: 3_level_0']['Pos'].str.contains('CB') == True) | (df['Unnamed: 3_level_0']['Pos'].str.contains('cb') == True)]
    df = df.sort_values(by=[('Games','GS')], ascending=False)
    df = df.reset_index(drop=True)[:2]
    df['PD/GS'] = df['Def Interceptions']['PD'].astype(float)/df['Games']['GS'].astype(float)
    returnList = [df['PD/GS'][0],df['PD/GS'][1]]
    return returnList

  def getLbVars(self,df_defense):
    df = df_defense.copy()
    df = df[(df['Unnamed: 3_level_0']['Pos'].str.contains('LB') == True) | (df['Unnamed: 3_level_0']['Pos'].str.contains('lb') == True)]
    df = df.sort_values(by=[('Games','GS')], ascending=False)
    df = df.reset_index(drop=True)[:2]
    df['TFL/GS'] = df['Tackles']['TFL'].astype(float)/df['Games']['GS'].astype(float)
    df['QBH/GS'] = df['Tackles']['QBHits'].astype(float)/df['Games']['GS'].astype(float)
    returnList = [df['TFL/GS'][0],df['QBH/GS'][0],df['TFL/GS'][1],df['QBH/GS'][1]]
    return returnList

  def getDefenseVars(self, df_defense):
    deVars = self.getDeVars(df_defense)
    dtVars = self.getDtVars(df_defense)
    sVars = self.getSVars(df_defense)
    cbVars = self.getCbVars(df_defense)
    lbVars = self.getLbVars(df_defense)
    return[*deVars,*dtVars,*sVars,*cbVars,*lbVars]


  def getTeamData(self, seasons, teams):
    off_cols = ('team','season','QB_Cmp%','QB_Int%','QB_Y/A','QB_Y/G','WR1_Y/Tgt','WR1_Ctch%',
        'WR1_R/G','WR2_Y/Tgt','WR2_Ctch%','WR2_R/G','RB1_Y/A','RB1_A/G','RB2_Y/A',
        'RB2_A/G','TE_Y/Tch','TE_Ctch%','TE_Y/Tch','OL_Sk%','KC_B40%',
        'KC_A40%','KC_Fgp')
    def_cols = ('teams','season','DE1_Tfl','DE1_Qbh','DE2_Tfl','DE2_Qbh',
    'DT1_Ct','DT1_Tfl','DT1_Qbh','DT2_Qbh',
    'S1_Pd','S1_Ct','S2_Pd','S2_Ct','CB1_Pd','CB2_Pd',
    'LB1_Tfl','LB1_Qbh','LB2_Tfl','LB2_Qbh')
    offense_master_df = pd.DataFrame()
    defense_master_df = pd.DataFrame()
    for year in seasons:
        print(year)
        for team in teams:
            time.sleep(.1)
            url = 'https://www.pro-football-reference.com/teams/'+team+'/'+str(year)+'.htm'
            result = requests.get(url).text
            result = result.replace('<!--',"")
            result = result.replace('--!>',"")
            df_passing = pd.read_html(result)[3]
            df_offense = pd.read_html(result)[4]
            df_kicking = pd.read_html(result)[6]
            df_defense = pd.read_html(result)[7]

            offenseVars = self.getOffenseVars(df_offense, df_passing, df_kicking)
            offenseVars = [float(x) for x in offenseVars]
            row = [team,year,*offenseVars]
            row_dict = dict(zip(off_cols,row))
            offense_master_df = offense_master_df.append(row_dict, ignore_index = True)

            defenseVars = self.getDefenseVars(df_defense)
            defenseVars = [float(x) for x in defenseVars]
            row = [team,year,*defenseVars]
            row_dict = dict(zip(def_cols,row))
            defense_master_df = defense_master_df.append(row_dict, ignore_index = True)

    return [offense_master_df,defense_master_df]


teams = ('crd','atl','rav','buf','car','chi','cin','cle','dal','den','det',
         'gnb','htx','clt','jax','kan','rai','sdg','ram','mia','min','nwe',
         'nor','nyg','nyj','phi','pit','sfo','sea','tam','oti','was')

seasons = range(2000,2022)
dataio = PlayerDataIO()
[offense, defense] = dataio.getTeamData(seasons,teams)
offense.to_csv('offense_data')
defense.to_csv('defense_data')