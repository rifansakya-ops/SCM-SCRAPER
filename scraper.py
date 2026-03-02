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
    "X-Requested-With": "XMLHttpRequest"
}

try:
    print("Mengambil token login...")
    # Langkah extra: Buka halaman login dulu untuk ambil cookies awal
    first_get = session.get("https://scm.nusadaya.net/login", headers=headers)
    
    print("Mencoba login...")
    login_data = {"username": user, "password": pw}
    # Nusadaya butuh referer agar tidak 401
    headers["Referer"] = "https://scm.nusadaya.net/login"
    
    login_resp = session.post("https://scm.nusadaya.net/login", data=login_data, headers=headers)
    
    if login_resp.status_code == 200:
        print("Login Selesai, mencoba tarik data...")
        all_rows = []
        for tahun in ["2025", "2026"]:
            print(f"Mengambil data tahun {tahun}...")
            params = {
                "draw": "1", "start": "0", "length": "500",
                "bidang": "", "tahun": tahun, "status_filter": ""
            }
            # Referer harus pindah ke halaman izin-prinsip agar diizinkan (Anti 401)
            headers["Referer"] = "https://scm.nusadaya.net/izin-prinsip"
            resp = session.get("https://scm.nusadaya.net/izin-prinsip/get-data", params=params, headers=headers)
            
            if resp.status_code == 200:
                data_json = resp.json()
                rows = data_json.get('data', [])
                all_rows.extend(rows)
                print(f"Berhasil menarik {len(rows)} data dari tahun {tahun}")
            else:
                print(f"Gagal di tahun {tahun}. Status: {resp.status_code}")

        # 3. Update Google Sheet
        if all_rows:
            worksheet.clear()
            header = ["Nomor Izin Prinsip", "Nilai / Jenis", "Project", "Keterangan", "Status", "Tgl Approve"]
            final_values = [header]
            for item in all_rows:
                final_values.append([
                    item.get('nomor_info', ''), item.get('nilai_info', ''),
                    item.get('project', ''), item.get('keterangan', ''),
                    item.get('status', ''), item.get('tgl_approve', '')
                ])
            worksheet.update(range_name='A1', values=final_values)
            print(f"DONE! {len(all_rows)} data masuk ke Google Sheet.")
        else:
            print("Tidak ada data ditemukan (Hasil Kosong).")
    else:
        print(f"Login Gagal. Status: {login_resp.status_code}")

except Exception as e:
    print(f"Terjadi error fatal: {e}")
