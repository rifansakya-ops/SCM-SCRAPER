import requests
import os
import json
import gspread
from google.oauth2.service_account import Credentials

# 1. Setup Google Sheets
gcp_json = os.getenv("GCP_SERVICE_ACCOUNT_KEY")
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(json.loads(gcp_json), scopes=scopes)
client = gspread.authorize(creds)

# Masukkan ID Sheet kamu di sini
SHEET_ID = "1AdveM0acH4q37GKnDYdyJ6l9p6m757zOp0UvquwxBjw"
sh = client.open_by_key(SHEET_ID)
worksheet = sh.get_worksheet(0)

# 2. Login Nusadaya
user = os.getenv("USERNAME")
pw = os.getenv("PASSWORD")
session = requests.Session()
login_url = "https://scm.nusadaya.net/login"
data_url = "https://scm.nusadaya.net/izin-prinsip/get-data"

headers = {"User-Agent": "Mozilla/5.0"}
params = {
    "draw": "2", "start": "0", "length": "100",
    "bidang": "01", "tahun": "2026", "status_filter": "approved"
}

try:
    print("Sedang login ke Nusadaya...")
    session.post(login_url, data={"username": user, "password": pw}, headers=headers)
    
    print("Mengambil data filter...")
    response = session.get(data_url, params=params, headers=headers)
    
    if response.status_code == 200:
        rows = response.json().get('data', [])
        
        # Siapkan data untuk dikirim ke Sheet
        final_data = []
        for item in rows:
            # Sesuaikan kunci kolom ini dengan hasil JSON dari web
            final_data.append([
                item.get('nomor_info'),
                item.get('nilai_info'),
                item.get('project'),
                item.get('status'),
                item.get('tgl_approve')
            ])
        
        # Masukkan ke Sheet mulai dari baris ke-2 (Baris 1 biasanya Judul)
        worksheet.clear() # Bersihkan dulu jika ingin data segar
        worksheet.update('A1', [["Nomor", "Nilai", "Project", "Status", "Tanggal"]]) # Header
        worksheet.update('A2', final_data)
        
        print(f"Berhasil! {len(final_data)} data masuk ke Google Sheets.")
    else:
        print("Gagal ambil data.")

except Exception as e:
    print(f"Error: {e}")
