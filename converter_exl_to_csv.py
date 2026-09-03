import pandas as pd
import os

# Папка с твоими Excel-файлами
input_dir = "stats"
output_dir = "stats_csv"
os.makedirs(output_dir, exist_ok=True)

for file in os.listdir(input_dir):
    if file.endswith(".xlsx"):
        # Читаем Excel
        df = pd.read_excel(os.path.join(input_dir, file), header=None)

        # Сохраняем как CSV
        csv_path = os.path.join(output_dir, file.replace(".xlsx", ".csv"))
        df.to_csv(csv_path, index=False, header=False)
        print(f"Сохранён: {csv_path}")