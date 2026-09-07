import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

row_statistic = pd.read_csv("all_matches_clean.csv")

# 1. Считаем общее количество очков каждой команды в каждом матче
team_totals = row_statistic.groupby(['game_id', 'team'])['points'].sum().reset_index(name='total_points')

# 2. Находим команду-победителя для каждого матча (по максимальным очкам)
winning_teams = team_totals.loc[
    team_totals.groupby('game_id')['total_points'].idxmax()
][['game_id', 'team']].rename(columns={'team': 'winning_team'})

# 3. Присоединяем информацию о победителе к основному датафрейму
row_statistic = row_statistic.merge(winning_teams, on='game_id', how='left')

# 4. Создаём колонку win (True, если команда игрока — победитель)
row_statistic['win'] = row_statistic['team'] == row_statistic['winning_team']

# 5. Удаляем временную колонку
row_statistic.drop(columns=['winning_team'], inplace=True)

print(row_statistic.mean(numeric_only=True))# среднее значение по каждой из числовых категорий
print(row_statistic.isna().sum().sum())# пропусков нет

corr_matrix = row_statistic.corr(numeric_only=True)
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.show()