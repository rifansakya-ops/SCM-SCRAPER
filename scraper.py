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

    SHEET_ID = "17ChoZhU5PImYt0J-3Y7F7l24yeQTABZ-EvZww32FFGs"
    sh = client.open_by_key(SHEET_ID)
    worksheet = sh.get_worksheet(0)
except Exception as e:
    print(f"Gagal koneksi ke Google Sheets: {e}")

# 2. Login Nusadaya
user = os.getenv("USERNAME")
pw = os.getenv("PASSWORD")
session = requests.Session()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

login_url = "https://scm.nusadaya.net/login"
data_url = "https://scm.nusadaya.net/izin-prinsip/get-data"

try:
    print("Mencoba login...")
    session.post(login_url, data={"username": user, "password": pw}, headers=headers)
    
    # Kumpulkan data dari tahun 2025 dan 2026 sekaligus agar tidak kosong
    all_rows = []
    for tahun in ["2025", "2026"]:
        print(f"Mengecek data tahun {tahun}...")
        params = {
            "draw": "2", "start": "0", "length": "500",
            "bidang": "01", "tahun": tahun, "status_filter": ""
        }
        resp = session.get(data_url, params=params, headers=headers)
        if resp.status_code == 200:
            data_tahun = resp.json().get('data', [])
            all_rows.extend(data_tahun)
            print(f"Ditemukan {len(data_tahun)} data di tahun {tahun}")

    # 3. Kirim ke Google Sheet
    worksheet.clear()
    header = ["Nomor Info", "Nilai", "Project", "Keterangan", "Status", "Tgl Approve"]
    final_data = [header]
    
    for item in all_rows:
        final_data.append([
            item.get('nomor_info'), item.get('nilai_info'),
            item.get('project'), item.get('keterangan'),
            item.get('status'), item.get('tgl_approve')
        ])
    
    if len(all_rows) > 0:
        worksheet.update(range_name='A1', values=final_data)
        print(f"TOTAL BERHASIL: {len(all_rows)} data terkirim ke Google Sheets!")
    else:
        # Jika benar-benar kosong, isi sheet dengan pesan ini agar kita tahu robotnya kerja
        worksheet.update(range_name='A1', values=[header, ["TIDAK ADA DATA DITEMUKAN DI WEB"]])
        print("Peringatan: Tidak ada data ditemukan di Nusadaya untuk 2025 & 2026.")

except Exception as e:
    print(f"Terjadi error: {e}")
