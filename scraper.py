import requests
import os
import json

# 1. Ambil kredensial dari GitHub Secrets
user = os.getenv("USERNAME")
pw = os.getenv("PASSWORD")

session = requests.Session()
login_url = "https://scm.nusadaya.net/login"

# URL dari filteran yang kamu temukan (Tanpa parameter di belakangnya agar lebih bersih)
data_url = "https://scm.nusadaya.net/izin-prinsip/get-data"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

payload = {
    "username": user,
    "password": pw
}

# Parameter filter dari URL yang kamu berikan
params = {
    "draw": "2",
    "start": "0",
    "length": "100",  # Mengambil 100 data pertama
    "bidang": "01",
    "tahun": "2026",
    "status_filter": "approved"
}

try:
    print("Mencoba login...")
    # Proses Login
    login_response = session.post(login_url, data=payload, headers=headers)
    
    if login_response.status_code == 200:
        print(f"Login Berhasil. Mencoba mengambil data filter...")
        
        # 2. Mengambil data menggunakan URL filter
        # Kita gunakan session.get karena URL yang kamu lampirkan adalah metode GET
        response = session.get(data_url, params=params, headers=headers)
        
        if response.status_code == 200:
            # Karena ini adalah get-data, hasilnya biasanya dalam format JSON
            data_json = response.json()
            
            # 3. Simpan hasil ke file .json agar struktur tabelnya terjaga
            with open("hasil_scrape.json", "w", encoding="utf-8") as f:
                json.dump(data_json, f, indent=4)
            
            total_data = data_json.get('recordsTotal', 0)
            print(f"Scraping Berhasil! Menemukan {total_data} data.")
        else:
            print(f"Gagal mengambil data filter. Status: {response.status_code}")
    else:
        print("Gagal login. Periksa Username/Password di GitHub Secrets.")

except Exception as e:
    print(f"Error: {e}")
