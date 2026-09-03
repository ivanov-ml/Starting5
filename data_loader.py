import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# ====== НАСТРОЙКИ ======
TEAM_URL = "https://ablforpeople.com/team/6475?seasonId=152&tournamentId=3249"
DOWNLOAD_DIR = os.path.abspath("stats")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ====== НАСТРОЙКА БРАУЗЕРА ======
options = Options()
prefs = {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

try:
    driver.get(TEAM_URL)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/game/']")))
    time.sleep(3)

    # Собираем ссылки на матчи
    game_links = []
    for a in driver.find_elements(By.CSS_SELECTOR, "a[href*='/game/']"):
        href = a.get_attribute("href")
        if href and "/game/" in href and "/statistic" not in href:
            if href.endswith("/"):
                href = href[:-1]
            game_links.append(f"{href}/statistic")

    print(f"Найдено матчей: {len(game_links)}")

    for i, link in enumerate(game_links, 1):
        print(f"[{i}/{len(game_links)}] Обработка: {link}")
        driver.get(link)
        time.sleep(2)

        try:
            # ШАГ 1: Находим кнопку "Документы" и кликаем
            docs_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Документы')]"))
            )
            docs_btn.click()
            print("  Меню 'Документы' открыто")
            time.sleep(1)

            # ШАГ 2: В открывшемся меню ищем "Статистика Excel" и кликаем
            excel_item = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Статистика Excel')]"))
            )
            excel_item.click()
            print("  Скачивание Excel запущено...")
            time.sleep(3)

        except Exception as e:
            print(f"  Ошибка: {e}")
            # Попробуем альтернативный поиск
            try:
                docs_btn = driver.find_element(By.CSS_SELECTOR, "button.download-btn")
                docs_btn.click()
                time.sleep(1)
                excel_item = driver.find_element(By.XPATH, "//*[contains(text(), 'Excel')]")
                excel_item.click()
                print("  Скачивание запущено (альтернативный способ)...")
                time.sleep(3)
            except Exception as e2:
                print(f"  Не удалось скачать: {e2}")

finally:
    driver.quit()