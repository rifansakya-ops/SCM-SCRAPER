import requests
import os
import gspread
from google.oauth2.service_account import Credentials
import json
import re # Tambahan untuk membersihkan teks

# Fungsi untuk membersihkan tag HTML agar teks di Sheet rapi
def clean_html(raw_html):
    if not raw_html: return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', str(raw_html))
    return cleantext.strip()

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
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://scm.nusadaya.net/izin-prinsip" # Penting agar server tidak curiga
}

all_rows = []
for tahun in ["2025", "2026"]:
    print(f"Menarik data tahun {tahun}...")
    url = "https://scm.nusadaya.net/izin-prinsip/get-data"
    params = {
        "draw": "1", "start": "0", "length": "500",
        "bidang": "", "tahun": tahun, "status_filter": ""
    }
    
    try:
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code == 200:
            data = resp.json().get('data', [])
            all_rows.extend(data)
            print(f"Berhasil: {len(data)} data ditemukan untuk {tahun}.")
        else:
            print(f"Gagal di {tahun}. Status: {resp.status_code}. Cek SESSION_COOKIE di GitHub Secret.")
    except Exception as e:
        print(f"Error saat tarik data {tahun}: {e}")

# 3. Update Google Sheet
if all_rows:
    worksheet.clear()
    header = ["Nomor Izin Prinsip", "Nilai / Jenis", "Project", "Keterangan", "Status", "Tgl Approve"]
    final_data = [header]
    
    for item in all_rows:
        # Gunakan clean_html agar tidak ada kode <b> atau <br> di Google Sheet
        final_data.append([
            clean_html(item.get('nomor_info', '')),
            clean_html(item.get('nilai_info', '')),
            clean_html(item.get('project', '')),
            clean_html(item.get('keterangan', '')),
            clean_html(item.get('status', '')),
            clean_html(item.get('tgl_approve', ''))
        ])
    
    worksheet.update(range_name='A1', values=final_data)
    print(f"SUKSES! Total {len(all_rows)} data terkirim ke Google Sheet.")
else:
    print("Data kosong. Periksa SESSION_COOKIE kamu, mungkin sudah kadaluwarsa.")
