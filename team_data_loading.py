import pandas as pd
import requests
import time

def getRbVars(df_offense):
  df = df_offense.droplevel(0,axis=1)
  df = df[(df['Pos'] == 'RB') | (df['Pos'] == 'rb')]
  df = df.sort_values(by=['GS'], ascending = False)
  df = df.reset_index(drop=True)[:2]
  returnList = [df['Y/A'][0],df['YScm'][0],df['Y/A'][1],df['YScm'][1]]
  return returnList

def getWrVars(df_offense):
  df = df_offense.droplevel(0,axis=1)
  df = df[(df['Pos'] == 'WR') | (df['Pos'] == 'wr')]
  df = df.sort_values(by=['GS'], ascending = False)
  df = df.reset_index(drop=True)[:2]
  returnList = [df['Y/Tgt'][0],float(df['Ctch%'][0][:-1]),df['YScm'][0],df['Y/Tgt'][1],float(df['Ctch%'][1][:-1]),df['YScm'][1]]
  return returnList

def getQbVars(df_passing):
  df = df_passing.copy()
  df = df[(df['Pos'] == 'QB') | (df['Pos'] == 'qb')]
  df = df.sort_values(by=['GS'], ascending = False)
  df = df.reset_index(drop=True)[:1]
  returnList = [df['Cmp%'][0],float(str(df['Int%'][0])[:-1]),df['Y/A'][0],df['Yds'][0]]
  return returnList

def getTeVars(df_offense):
  df = df_offense.droplevel(0,axis=1)
  df = df[(df['Pos'] == 'TE') | (df['Pos'] == 'te')]
  df = df.sort_values(by=['GS'], ascending = False)
  df = df.reset_index(drop=True)[:1]
  df = df[['Player','Y/Tch','Ctch%','YScm']]
  returnList = [df['Y/Tch'][0],float(df['Ctch%'][0][:-1]),df['YScm'][0]]
  return returnList

def getOlVars(df_passing):
  df = df_passing.copy()
  sacks = df['Sk'].values.sum()
  lost_yards = df['Yds.1'].sum()
  return [sacks,lost_yards]

def getKcVars(df_kicking):
  df = df_kicking.copy()
  df = df.sort_values(by=[('Scoring','FGA')], ascending = False)
  df = df.reset_index(drop=True)[:1]
  fg_b40 = (float(df['20-29']['FGA']) + float(df['30-39']['FGA'])) / (float(df['20-29']['FGM']) + float(df['30-39']['FGM']))
  fg_a40 = (float(df['40-49']['FGA']) + float(df['50+']['FGA'])) / (float(df['40-49']['FGM']) + float(df['50+']['FGM']))
  fga = float(df['Scoring']['FGA'])
  return [fg_b40,fg_a40,fga]

def getOffenseVars(df_offense,df_passing,df_kicking):
  rbVars = getRbVars(df_offense)
  wrVars = getWrVars(df_offense)
  qbVars = getQbVars(df_passing)
  teVars = getTeVars(df_offense)
  olVars = getOlVars(df_passing)
  kcVars = getKcVars(df_kicking)

  return[*qbVars,*wrVars,*rbVars,*teVars,*olVars,*kcVars]


cols = ('team','season','QB_Cmp%','QB_Int%','QB_Y/A','QB_Yds','WR1_Y/Tgt','WR1_Ctch%',
        'WR1_YScm','WR2_Y/Tgt','WR2_Ctch%','WR2_YScm','RB1_Y/A','RB1_YScm','RB2_Y/A',
        'RB2_YScm','TE_Y/Tch','TE_Ctch%','TE_YScm','OL_Sk','OL_Lyds','KC_B40%',
        'KC_A40%','KC_Fga')

teams = ('crd','atl','rav','buf','car','chi','cin','cle','dal','den','det',
         'gnb','htx','clt','jax','kan','rai','sdg','ram','mia','min','nwe',
         'nor','nyg','nyj','phi','pit','sfo','sea','tam','oti','was')

seasons = range(2021,2022)
  
master_df = pd.DataFrame()

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

        offenseVars = getOffenseVars(df_offense, df_passing, df_kicking)
        offenseVars = [float(x) for x in offenseVars]
        row = [team,year,*offenseVars]
        row_dict = dict(zip(cols,row))
        master_df = master_df.append(row_dict, ignore_index = True)

master_df.to_csv('offense_data_2020_2021')