# QRFile Share – Transfer File Lokal via QR Code 📱💻

Aplikasi web sederhana untuk transfer file dari laptop ke HP (dan sebaliknya) melalui jaringan lokal **tanpa cloud**, cukup dengan **scan QR Code**.  
Tanpa akun, tanpa instalasi aplikasi tambahan.

---

## 🔧 Fitur Utama

- 📤 Upload file dari browser desktop
- 📱 Scan QR Code dari kamera HP untuk download langsung
- 🌐 Berjalan di jaringan lokal (misalnya Wi-Fi rumah)
- 🕒 File otomatis terhapus setelah satu kali download atau 10 menit
- 🧱 Antarmuka minimalis dan responsif
- ❌ Tanpa login, tanpa database, tanpa JavaScript berlebihan

---

## 🚀 Cara Menjalankan

1. **Clone repository:**
   ```bash
   git clone https://github.com/zerquix/qrfile-share.git
   cd qrfile-share

## 2. (Opsional) Buat virtual environment:
``` bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

## 3. Install dependency:
```
pip install -r requirements.txt

```
## 4. Jalankan server lokal:
```
python app.py

```
## 5. Akses di browser:
```
http://localhost:8000

atau dari perangkat lain: http://192.168.x.x:8000 (IP lokal)
```




---

# 🗂️ Struktur Folder

qrfile-share/
├── app.py                   # Backend utama (Flask)
├── templates/
│   └── index.html           # Halaman upload & QR
├── static/
│   └── qrcode.png           # Hasil QR Code
├── uploads/                 # Folder penyimpanan file
├── requirements.txt         # Daftar dependensi
└── README.md                # Dokumentasi ini


---

# ⚙️ Pengaturan Opsional

Durasi penyimpanan file bisa diubah di app.py:

FILE_EXPIRY_SECONDS = 600  # default: 10 menit

Download otomatis hapus file: aktif secara default

Untuk akses dari luar jaringan lokal, gunakan:

ngrok http 8000



---

## 📦 Teknologi Digunakan

Python 3

Flask

qrcode (dengan Pillow)

HTML + CSS sederhana (tanpa Bootstrap, tanpa JavaScript berat)



---

## 🛡️ Lisensi

Proyek ini dirilis di bawah lisensi MIT. Silakan digunakan dan dimodifikasi.


---

## 🤝 Kontribusi

Pull request terbuka untuk fitur seperti:

CLI uploader

Dockerfile

Password download

QR dengan expiry time embed



---

## 📸 Demo

<img src="static/qrcode.png" alt="QR Code Example" width="200">
---

## 🔗 Repo & Kontak

GitHub: github.com/zerquix/qrfile-share

Buka Issue jika ada pertanyaan, bug, atau saran pengembangan.


---

> Aplikasi ini dirancang untuk digunakan secara lokal tanpa ketergantungan pada cloud atau akun login.

