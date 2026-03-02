import requests
import os
import json
import gspread
from google.oauth2.service_account import Credentials

# 1. Setup Google Sheets
# Mengambil kunci JSON dari GitHub Secret
gcp_json = os.getenv("GCP_SERVICE_ACCOUNT_KEY")
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(json.loads(gcp_json), scopes=scopes)
client = gspread.authorize(creds)

# Menggunakan ID Sheet yang baru kamu berikan
SHEET_ID = "17ChoZhU5PImYt0J-3Y7F7l24yeQTABZ-EvZww32FFGs"
sh = client.open_by_key(SHEET_ID)
worksheet = sh.get_worksheet(0) # Mengakses tab pertama

# 2. Login Nusadaya
user = os.getenv("USERNAME")
pw = os.getenv("PASSWORD")
session = requests.Session()
login_url = "https://scm.nusadaya.net/login"
# URL target yang kamu temukan di tab Network tadi
data_url = "https://scm.nusadaya.net/izin-prinsip/get-data"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Parameter filter sesuai data yang kamu berikan sebelumnya
params = {
    "draw": "2",
    "start": "0",
    "length": "100",
    "bidang": "01",
    "tahun": "2026",
    "status_filter": "approved"
}

try:
    print("Mencoba login ke Nusadaya...")
    session.post(login_url, data={"username": user, "password": pw}, headers=headers)
    
    print(f"Mengambil data filter (Tahun: {params['tahun']})...")
    response = session.get(data_url, params=params, headers=headers)
    
    if response.status_code == 200:
        data_json = response.json()
        rows = data_json.get('data', []) # Mengambil baris data dari JSON
        
        # 3. Membersihkan dan Memasukkan data ke Google Sheet
        worksheet.clear() # Menghapus data lama agar tidak tumpang tindih
        
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
        
        # Kirim data ke Google Sheet
        worksheet.update('A1', all_values)
        print(f"Berhasil! {len(rows)} data telah dikirim ke Google Sheet.")
    else:
        print(f"Gagal mengambil data. Status code: {response.status_code}")

except Exception as e:
    print(f"Terjadi kesalahan: {e}")
