import requests
from bs4 import BeautifulSoup
import os

# Ambil kredensial
user = os.getenv("USERNAME")
pw = os.getenv("PASSWORD")

session = requests.Session()
login_url = "https://scm.nusadaya.net/login"
target_url = "https://scm.nusadaya.net/home" 

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

payload = {
    "username": user,
    "password": pw
}

try:
    print("Mencoba login...")
    session.post(login_url, data=payload, headers=headers)
    response = session.get(target_url, headers=headers)
    
    # Ambil teks sedikit untuk bukti berhasil
    hasil = response.text[:500] 

    with open("hasil_scrape.txt", "w", encoding="utf-8") as f:
        f.write(hasil)
    print("Scraping berhasil!")
except Exception as e:
    print(f"Error: {e}")
