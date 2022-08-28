import pandas as pd

gameString = 'game_data'
defString = 'defense_data'
offString = 'offense_data'

df_game = pd.read_csv(gameString)
df_off = pd.read_csv(offString)
df_def = pd.read_csv(defString)

df_merged = df_game.merge(df_off,left_on=['season','OffenseTeam'],right_on=['season','team'])
df_merged = df_merged.merge(df_def,left_on=['season','DefenseTeam'],right_on=['season','teams'])
#drops redundant columns
df_merged = df_merged.drop(['Unnamed: 0_x','Unnamed: 0_y','team','Unnamed: 0','teams'],axis=1)

df_merged.to_csv('merged_data')



