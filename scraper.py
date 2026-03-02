import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests

# 1. Konfigurasi Chrome Headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    print("Membuka halaman login Nusadaya...")
    driver.get("https://scm.nusadaya.net/login")

    # 2. Menunggu kotak login muncul (Maksimal 20 detik)
    wait = WebDriverWait(driver, 20)
    user_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    
    print("Mengisi kredensial...")
    user_field.send_keys(os.getenv("USERNAME"))
    driver.find_element(By.NAME, "password").send_keys(os.getenv("PASSWORD"))
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # 3. Tunggu proses login selesai
    time.sleep(10) 

    # 4. Ambil Cookie otomatis dari browser
    cookies = driver.get_cookies()
    session_cookie = "; ".join([f"{c['name']}={c['value']}" for c in cookies])

    all_data = []
    headers = {
        "Cookie": session_cookie,
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://scm.nusadaya.net/izin-prinsip"
    }

    # 5. Tarik data tahun 2025 & 2026
    for tahun in ["2025", "2026"]:
        print(f"Menarik data tahun {tahun}...")
        api_url = f"https://scm.nusadaya.net/izin-prinsip/get-data?draw=1&start=0&length=1000&bidang=&tahun={tahun}&status_filter="
        resp = requests.get(api_url, headers=headers)
        if resp.status_code == 200:
            all_data.extend(resp.json().get('data', []))

    # 6. Simpan hasil akhir ke data.json
    with open('data.json', 'w') as f:
        json.dump(all_data, f, indent=4)
    print(f"SUKSES! {len(all_data)} data disimpan ke data.json")

except Exception as e:
    print(f"TERJADI ERROR: {e}")
    driver.save_screenshot("error_screenshot.png") # Untuk cek jika gagal

finally:
    driver.quit()
