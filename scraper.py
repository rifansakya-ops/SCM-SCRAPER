import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests

# Konfigurasi agar browser berjalan di latar belakang (Headless)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    print("Membuka Nusadaya...")
    driver.get("https://scm.nusadaya.net/login")
    time.sleep(3)

    print("Proses Login otomatis...")
    driver.find_element(By.NAME, "username").send_keys(os.getenv("USERNAME"))
    driver.find_element(By.NAME, "password").send_keys(os.getenv("PASSWORD"))
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(5)

    # Mengambil Cookie dari sesi login browser tadi secara otomatis
    cookies = driver.get_cookies()
    session_cookie = "; ".join([f"{c['name']}={c['value']}" for c in cookies])

    all_data = []
    headers = {"Cookie": session_cookie, "X-Requested-With": "XMLHttpRequest"}

    # Menarik data tahun 2025 dan 2026 sesuai gambar Anda
    for tahun in ["2025", "2026"]:
        print(f"Mengambil data {tahun}...")
        api_url = f"https://scm.nusadaya.net/izin-prinsip/get-data?draw=1&start=0&length=1000&bidang=&tahun={tahun}&status_filter="
        resp = requests.get(api_url, headers=headers)
        if resp.status_code == 200:
            all_data.extend(resp.json().get('data', []))

    # Menyimpan hasil akhir ke file data.json (BUKAN file .txt lagi)
    with open('data.json', 'w') as f:
        json.dump(all_data, f, indent=4)
    print(f"Berhasil! {len(all_data)} data disimpan ke data.json")

finally:
    driver.quit()
