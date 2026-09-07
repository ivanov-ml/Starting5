import pandas as pd
import os
import re

def parse_basketball_excel(file_path, output_dir):
    """Преобразует Excel-файл со статистикой матча в структурированный CSV"""

    # Читаем файл без заголовков
    df_raw = pd.read_excel(file_path, header=None, dtype=str)
    data = df_raw.values.tolist()

    # 1. Извлекаем название матча (первая строка)
    match_name = data[0][0] if data and data[0] else ""
    # Ищем тире, чтобы разделить команды
    teams = []
    if " - " in match_name:
        teams = [t.strip() for t in match_name.split(" - ")]
    else:
        # если не удалось, пробуем найти команды по словам "Mosmade" и "Крылья"
        if "Mosmade" in match_name:
            teams = ["Mosmade", "Крылья"]  # пример, можно автоматизировать

    if len(teams) < 2:
        print(f"⚠️ Не удалось определить команды в файле {file_path}")
        return

    team1, team2 = teams[0], teams[1]

    # 2. Находим блоки команд
    def find_team_block(rows, team_name, start_search=0):
        """Ищет строку с названием команды, затем заголовок с '№' и 'Фамилия Имя'"""
        team_start = -1
        for i in range(start_search, len(rows)):
            if rows[i] and rows[i][0] and team_name in str(rows[i][0]):
                team_start = i
                break
        if team_start == -1:
            return None

        # Ищем заголовок (строку с '№' и 'Фамилия Имя')
        header_row = -1
        for i in range(team_start, min(team_start + 10, len(rows))):
            if rows[i] and any("№" in str(cell) for cell in rows[i]) and any("Фамилия Имя" in str(cell) for cell in rows[i]):
                header_row = i
                break
        if header_row == -1:
            return None

        # Заголовок — первая строка
        header = rows[header_row]
        # Вторая строка (подзаголовок) — часто идёт следом
        sub_header = rows[header_row + 1] if header_row + 1 < len(rows) else []

        # Формируем имена колонок: объединяем первую и вторую строки
        columns = []
        for i, col in enumerate(header):
            col_name = str(col).strip() if col else ""
            # Если есть подзаголовок и он не пустой, добавляем его в скобках
            sub = str(sub_header[i]).strip() if i < len(sub_header) and sub_header[i] else ""
            if sub and sub not in col_name:
                col_name = f"{col_name}_{sub}" if col_name else sub
            elif not col_name and sub:
                col_name = sub
            col_name = col_name.replace(" ", "_").replace("/", "_")  # чистим
            columns.append(col_name)

        # Теперь собираем строки данных до "Итого"
        data_start = header_row + 2
        data_rows = []
        for i in range(data_start, len(rows)):
            row = rows[i]
            if not row or all(str(cell).strip() in ("", "nan", "None") for cell in row):
                continue
            # Проверяем, не итоговая ли строка
            if any(str(cell).strip() == "Итого" for cell in row):
                break
            # Если строка похожа на игрока (первая колонка — цифра или число)
            if row[0] and re.match(r'^\d+$', str(row[0]).strip()):
                # Убедимся, что длина строки соответствует колонкам
                if len(row) < len(columns):
                    row.extend([""] * (len(columns) - len(row)))
                data_rows.append(row[:len(columns)])

        if not data_rows:
            return None

        # Создаём DataFrame
        df = pd.DataFrame(data_rows, columns=columns)
        df['team'] = team_name
        return df

    # Ищем блоки для каждой команды (передаём разные индексы начала поиска)
    df1 = find_team_block(data, team1, 0)
    # Для второй команды начинаем поиск после места, где нашли первую
    if df1 is not None:
        # можно искать вторую команду после первой
        df2 = find_team_block(data, team2, df1.index[-1] if len(df1) > 0 else 0)
    else:
        df2 = find_team_block(data, team2, 0)

    # Объединяем
    df_all = pd.DataFrame()
    if df1 is not None:
        df_all = pd.concat([df_all, df1], ignore_index=True)
    if df2 is not None:
        df_all = pd.concat([df_all, df2], ignore_index=True)

    if df_all.empty:
        print(f"⚠️ Не удалось извлечь данные из файла {file_path}")
        return

    # Удаляем колонку с пустым названием (если есть)
    df_all = df_all.drop(columns=[col for col in df_all.columns if col == ""], errors='ignore')

    # Сохраняем
    base_name = os.path.basename(file_path).replace(".xlsx", "")
    csv_path = os.path.join(output_dir, f"{base_name}.csv")
    df_all.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"✅ Сохранён: {csv_path} ({len(df_all)} строк)")

if __name__ == "__main__":
    input_dir = "stats"  # папка с Excel-файлами
    output_dir = "stats_csv"  # папка для CSV
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.endswith(".xlsx"):
            parse_basketball_excel(os.path.join(input_dir, file), output_dir)