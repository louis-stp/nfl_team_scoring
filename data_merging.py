import pandas as pd

gameString = 'game_odds'
defString = 'defense_data'
offString = 'offense_data'

df_game = pd.read_csv(gameString)
df_off = pd.read_csv(offString)
df_def = pd.read_csv(defString)

df_merged = df_game.merge(df_off,left_on=['season','favorite'],right_on=['season','team'])
df_merged = df_merged.merge(df_def,left_on=['season','favorite'],right_on=['season','teams'])
df_merged = df_merged.merge(df_off,left_on=['season','underdog'],right_on=['season','team'])
df_merged = df_merged.merge(df_def,left_on=['season','underdog'],right_on=['season','teams'])
#drops redundant columns
df_merged = df_merged.drop(['Unnamed: 0_x','Unnamed: 0_y','Unnamed: 0','team_x','teams_x','team_y','teams_y'],axis=1)

df_merged.to_csv('merged_data')



