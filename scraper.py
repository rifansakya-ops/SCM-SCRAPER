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
    sh = client.open_by_key("17ChoZhU5PImYt0J-3Y7F7l24yeQTABZ-EvZww32FFGs")
    worksheet = sh.get_worksheet(0)
except Exception as e:
    print(f"Gagal koneksi ke Google Sheets: {e}")

# 2. Login & Scrape Nusadaya
user = os.getenv("USERNAME")
pw = os.getenv("PASSWORD")
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-Requested-With": "XMLHttpRequest" # Memberitahu server ini permintaan data
}

try:
    print("Mencoba login...")
    session.post("https://scm.nusadaya.net/login", data={"username": user, "password": pw}, headers=headers)
    
    all_rows = []
    # Kita cek 2025 dan 2026 seperti di browser
    for tahun in ["2025", "2026"]:
        print(f"Mengambil data tahun {tahun}...")
        # Parameter disesuaikan dengan gambar image_4f5fa6.png (Semua Bidang & Semua Status)
        params = {
            "draw": "1",
            "start": "0",
            "length": "100",
            "bidang": "",         # Kosong = Semua Bidang (seperti di gambar)
            "tahun": tahun,       # Sesuai pilihan tahun
            "status_filter": ""   # Kosong = Semua Status (termasuk Menunggu Verifikasi)
        }
        
        resp = session.get("https://scm.nusadaya.net/izin-prinsip/get-data", params=params, headers=headers)
        
        if resp.status_code == 200:
            try:
                data_json = resp.json()
                rows = data_json.get('data', [])
                all_rows.extend(rows)
                print(f"Berhasil menarik {len(rows)} data dari tahun {tahun}")
            except:
                print(f"Format data tahun {tahun} tidak dikenali.")
        else:
            print(f"Server menolak permintaan tahun {tahun}. Status: {resp.status_code}")

    # 3. Update Google Sheet
    worksheet.clear()
    header = ["Nomor Izin Prinsip", "Nilai / Jenis", "Project", "Keterangan", "Status", "Tgl Approve"]
    final_values = [header]
    
    for item in all_rows:
        # Kita ambil data sesuai kolom di gambar image_4f5fa6.png
        final_values.append([
            item.get('nomor_info', ''),
            item.get('nilai_info', ''),
            item.get('project', ''),
            item.get('keterangan', ''),
            item.get('status', ''),
            item.get('tgl_approve', '')
        ])
    
    if len(all_rows) > 0:
        worksheet.update(range_name='A1', values=final_values)
        print(f"DONE! {len(all_rows)} data sudah masuk ke Google Sheet.")
    else:
        print("Robot jalan, tapi tidak menemukan data apapun di web.")

except Exception as e:
    print(f"Terjadi error fatal: {e}")
