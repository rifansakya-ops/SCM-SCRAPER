import requests
import os
import json
import gspread
from google.oauth2.service_account import Credentials

# 1. Setup Google Sheets
try:
    gcp_json = os.getenv("GCP_SERVICE_ACCOUNT_KEY")
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(json.loads(gcp_json), scopes=scopes)
    client = gspread.authorize(creds)

    # Menggunakan ID Sheet kamu yang terbaru
    SHEET_ID = "17ChoZhU5PImYt0J-3Y7F7l24yeQTABZ-EvZww32FFGs"
    sh = client.open_by_key(SHEET_ID)
    worksheet = sh.get_worksheet(0) # Mengakses tab pertama
except Exception as e:
    print(f"Gagal Setup Google Sheets: {e}")

# 2. Login Nusadaya
user = os.getenv("USERNAME")
pw = os.getenv("PASSWORD")
session = requests.Session()
login_url = "https://scm.nusadaya.net/login"
data_url = "https://scm.nusadaya.net/izin-prinsip/get-data"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Parameter diperbaiki: Tahun 2025 dan Status dikosongkan untuk tes
params = {
    "draw": "2",
    "start": "0",
    "length": "500",      # Mengambil lebih banyak baris
    "bidang": "01",
    "tahun": "2025",      # Tes dengan 2025 karena 2026 mungkin masih kosong
    "status_filter": ""   # Kosongkan agar semua status (Approved/Pending) muncul
}

try:
    print("Mencoba login ke Nusadaya...")
    session.post(login_url, data={"username": user, "password": pw}, headers=headers)
    
    print(f"Mengambil data filter (Tahun: {params['tahun']}, Semua Status)...")
    response = session.get(data_url, params=params, headers=headers)
    
    if response.status_code == 200:
        data_json = response.json()
        rows = data_json.get('data', [])
        
        # 3. Membersihkan dan Memasukkan data ke Google Sheet
        worksheet.clear() 
        
        # Header kolom
        header = ["Nomor Info", "Nilai", "Project", "Keterangan", "Status", "Tgl Approve"]
        all_values = [header]
        
        for item in rows:
            line = [
                item.get('nomor_info'),
                item.get('nilai_info'),
                item.get('project'),
                item.get('keterangan'),
                item.get('status'),
                item.get('tgl_approve')
            ]
            all_values.append(line)
        
        # Update ke Sheet (Menggunakan sintaks terbaru)
        worksheet.update(range_name='A1', values=all_values)
        print(f"Berhasil! {len(rows)} data telah dikirim ke Google Sheet.")
    else:
        print(f"Gagal mengambil data. Status code: {response.status_code}")

except Exception as e:
    print(f"Terjadi kesalahan: {e}")
