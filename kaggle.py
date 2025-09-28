import os
from pathlib import Path
import kagglehub

# This will download the latest version
path = kagglehub.dataset_download("abecklas/fifa-world-cup")

print("Returned path:", path)
print("Current working directory:", os.getcwd())

data_path = Path(path) if path else (Path(__file__).parent / "input")

import pandas as pd
import matplotlib.pyplot as plt

#GOALS SCORED STATS
plt.figure(figsize=(10,6)) 
plt.plot(df['Year'], df['GoalsScored'], marker='o', color='green')
plt.title('Change in numbers of goals scored')
plt.xlabel('Year')
plt.ylabel('Goals Scored')
plt.grid(True)
plt.show()


#ATTENDANCE STATS 
df['Attendance'] = df['Attendance'].str.replace('.', '', regex=False).astype(int)

plt.figure(figsize=(10, 6))
plt.bar(df['Year'], df['Attendance'], color='orange')
plt.title("Total attendance per Year")
plt.xlabel("Year")
plt.ylabel("Spectators")
plt.grid(axis='y')
plt.show()

# WINNNERS OF THE COMPETITION
print(df['Winner'].value_counts())

#REOCCURING FINALISTS
print(df['Runners-Up'].value_counts())

# HIGHEST THIRD PLACE PLACERS
print(df['Third'].value_counts())

# TOTAL NUMBER OF WORLD CUP PLAYERS
candidates_players = [
	data_path / 'WorldCupPlayers.csv',
	Path(__file__).parent / 'input' / 'WorldCupPlayers.csv',
	Path('input') / 'WorldCupPlayers.csv'
]

csv_players = next((p for p in candidates_players if p.exists()), None)
if csv_players is None:
	print("Could not find WorldCupPlayers.csv. Checked:")
	for p in candidates_players:
		print(" -", p)
	total_players = 0
else:
	print(f"Loading players CSV from: {csv_players}")
	df_players = pd.read_csv(csv_players)
	
	if 'MatchID' in df_players.columns and 'Player Name' in df_players.columns:
		players_per_match = df_players.groupby('MatchID')['Player Name'].count()
		total_players = players_per_match.sum()
	elif 'Player Name' in df_players.columns:
		total_players = df_players['Player Name'].nunique(dropna=True)
	else:
		total_players = len(df_players)

print(f"Number of total players : {total_players}")

if lineup_col:
	lineup_counts = df_players[lineup_col].value_counts()
	print(f"Using lineup column: '{lineup_col}'")
	print(lineup_counts)

	# Graph for this
	lineup_counts.plot(kind='bar', title='Players in Lineup vs Substitutes')
	plt.xlabel('Starters vs Substitutes')
	plt.ylabel('Number of Players')
	plt.show()

#GOALS SCORED PER MIN
import re

df_goals = df_players[df_players['Event'].notna()]
df_goals = df_goals[df_goals['Event'].str.contains(r"G\d+", regex=True, na=False)]

minutes = df_goals['Event'].str.extract(r"G(\d+)", expand=False)
goal_minutes = pd.to_numeric(minutes, errors='coerce').dropna().astype(int)

# GRAPH
goal_minutes.hist(bins=9, figsize=(10,5), color='purple', edgecolor='black')
plt.title('Goal Minutes Distribution')
plt.xlabel('Minutes')
plt.ylabel('Number of Goals')
plt.grid(True)
plt.show()

# Coaches with most World Cup Appearances
top_coaches = df_players['Coach Name'].value_counts().head(20)
print(top_coaches)

# Players with most games played
top_players = df_players['Player Name'].value_counts().head(10)
print(top_players)

