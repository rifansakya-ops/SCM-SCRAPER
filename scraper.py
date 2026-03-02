import requests
import os
import gspread
from google.oauth2.service_account import Credentials
import json

# 1. Koneksi ke Google Sheets
try:
    gcp_json = os.getenv("GCP_SERVICE_ACCOUNT_KEY")
    creds = Credentials.from_service_account_info(json.loads(gcp_json), scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    sh = client.open_by_key("17ChoZhU5PImYt0J-3Y7F7l24yeQTABZ-EvZww32FFGs")
    worksheet = sh.get_worksheet(0)
except Exception as e:
    print(f"Error Koneksi Sheet: {e}")

# 2. Ambil Data Menggunakan Cookie Manual
cookie_manual = os.getenv("SESSION_COOKIE")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Cookie": cookie_manual,
    "X-Requested-With": "XMLHttpRequest"
}

all_rows = []
# Kita cek 2025 dan 2026
for tahun in ["2025", "2026"]:
    print(f"Menarik data tahun {tahun}...")
    # URL menggunakan struktur yang kamu berikan
    url = "https://scm.nusadaya.net/izin-prinsip/get-data"
    params = {
        "draw": "1",
        "start": "0",
        "length": "500",  # Ambil banyak sekaligus
        "bidang": "",     # Semua bidang
        "tahun": tahun,
        "status_filter": "" # Kosongkan agar yang "Menunggu Verifikasi" juga masuk
    }
    
    try:
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code == 200:
            data = resp.json().get('data', [])
            all_rows.extend(data)
            print(f"Berhasil: {len(data)} data ditemukan.")
        else:
            print(f"Gagal. Status: {resp.status_code}. Cek apakah Cookie sudah expired.")
    except Exception as e:
        print(f"Error saat tarik data: {e}")

# 3. Update Google Sheet
if all_rows:
    worksheet.clear()
    header = ["Nomor Izin Prinsip", "Nilai / Jenis", "Project", "Keterangan", "Status", "Tgl Approve"]
    final_data = [header]
    
    for item in all_rows:
        # Menyesuaikan dengan kolom di URL kamu
        final_data.append([
            item.get('nomor_info', ''),
            item.get('nilai_info', ''),
            item.get('project', ''),
            item.get('keterangan', ''),
            item.get('status', ''),
            item.get('tgl_approve', '')
        ])
    
    worksheet.update(range_name='A1', values=final_data)
    print(f"SUKSES! Total {len(all_rows)} data terkirim.")
else:
    print("Data kosong. Periksa apakah Cookie di GitHub Secret sudah benar.")
