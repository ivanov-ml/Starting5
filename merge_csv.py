import pandas as pd
import os

input_dir = "stats_csv"
output_file = "all_matches_clean.csv"

all_data = []
for file in os.listdir(input_dir):
    if file.endswith(".csv"):
        df = pd.read_csv(os.path.join(input_dir, file), encoding='utf-8-sig')
        game_id = file.replace(".csv", "")
        df['game_id'] = game_id
        all_data.append(df)

if all_data:
    merged = pd.concat(all_data, ignore_index=True)

    # Переименовываем колонки
    new_columns = [
        'number',
        'player_name',
        'points',
        'two_attempts',
        'two_percent',
        'three_attempts',
        'three_percent',
        'ft_attempts',
        'ft_percent',
        'assists',
        'steals',
        'blocks',
        'def_rebounds',
        'off_rebounds',
        'total_rebounds',
        'turnovers',
        'fouls',
        'fouls_drawn',
        'time_played',
        'plus_minus',
        'team',
        'game_id'
    ]

    # Проверяем, что количество колонок совпадает
    if len(merged.columns) == len(new_columns):
        merged.columns = new_columns
    else:
        print(f"⚠️ Количество колонок не совпадает: {len(merged.columns)} vs {len(new_columns)}")
        print("Пропускаем переименование")

    merged.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✅ Очищенный файл сохранён: {output_file}, строк: {len(merged)}")
else:
    print("⚠️ Нет файлов для объединения")