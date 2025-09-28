import os
from pathlib import Path
import kagglehub

# This will download the latest version
path = kagglehub.dataset_download("abecklas/fifa-world-cup")

print("Returned path:", path)
print("Current working directory:", os.getcwd())

# Normalize returned value into a Path object. If the function returned None,
# fall back to the repository `input/` folder next to this script.
data_path = Path(path) if path else (Path(__file__).parent / "input")

if data_path.exists():
	if data_path.is_dir():
		print(f"Dataset directory exists: {data_path}")
		for p in sorted(data_path.iterdir()):
			print(" -", p.name)
	else:
		print(f"Downloaded file: {data_path.name} (path: {data_path})")
else:
	print("ERROR: path does not exist:", data_path)
	

import pandas as pd

# Try to find the CSV in a few sensible locations. Prefer the downloaded/returned
# dataset folder (data_path) but also check the repo `input/` folder.
candidates = [
	data_path / 'WorldCups.csv',
	Path(__file__).parent / 'input' / 'WorldCups.csv',
	Path('input') / 'WorldCups.csv'
]

csv_path = None
for c in candidates:
	if c.exists():
		csv_path = c
		break

if csv_path is None:
	# Show helpful diagnostics to fix path problems quickly
	looked = '\n'.join(str(p) for p in candidates)
	raise FileNotFoundError(
		f"Could not find WorldCups.csv. Checked these locations:\n{looked}\n\n"
		f"Current working directory: {os.getcwd()}\n"
		f"Dataset folder (data_path) was: {data_path}\n"
	)

print(f"Loading CSV from: {csv_path}")
df = pd.read_csv(csv_path)

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

	# Preferred columns: 'MatchID' and 'Player Name'
	if 'MatchID' in df_players.columns and 'Player Name' in df_players.columns:
		players_per_match = df_players.groupby('MatchID')['Player Name'].count()
		total_players = players_per_match.sum()
	elif 'Player Name' in df_players.columns:
		total_players = df_players['Player Name'].nunique(dropna=True)
	else:
		# Fallback: use row count
		total_players = len(df_players)

print(f"Number of total players : {total_players}")

# Players in the lineup vs substitutes (robust to column name differences)
possible_lineup_cols = ['Line_Up', 'Line Up', 'Line-Up', 'LineUp', 'IsStarter', 'Starter', 'Starting']
lineup_col = next((c for c in possible_lineup_cols if c in df_players.columns), None)

if lineup_col:
	lineup_counts = df_players[lineup_col].value_counts()
	print(f"Using lineup column: '{lineup_col}'")
	print(lineup_counts)

	# Graph for this
	lineup_counts.plot(kind='bar', title='Players in Lineup vs Substitutes')
	plt.xlabel('Starters vs Substitutes')
	plt.ylabel('Number of Players')
	plt.show()
else:
	print("No lineup-like column found in players CSV. Available columns:")
	print(df_players.columns.tolist())

#GOALS SCORED PER MIN
import re

df_goals = df_players[df_players['Event'].notna()]
df_goals = df_goals[df_goals['Event'].str.contains(r"G\d+", regex=True, na=False)]

# Extract minute numbers from patterns like "G12'" or "G90+1'". We capture the main minute
# part (e.g. 12 or 90) and coerce to numeric, dropping any non-matches.
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