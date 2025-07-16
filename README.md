# QRFile Share â€“ Transfer File Lokal via QR Code ðŸ“±ðŸ’»

Aplikasi web sederhana untuk transfer file dari laptop ke HP (dan sebaliknya) melalui jaringan lokal **tanpa cloud**, cukup dengan **scan QR Code**.  
Tanpa akun, tanpa instalasi aplikasi tambahan.

---

## ðŸ”§ Fitur Utama

- ðŸ“¤ Upload file dari browser desktop
- ðŸ“± Scan QR Code dari kamera HP untuk download langsung
- ðŸŒ Berjalan di jaringan lokal (misalnya Wi-Fi rumah)
- ðŸ•’ File otomatis terhapus setelah satu kali download atau 10 menit
- ðŸ§± Antarmuka minimalis dan responsif
- âŒ Tanpa login, tanpa database, tanpa JavaScript berlebihan

---

## ðŸš€ Cara Menjalankan

1. **Clone repository:**
   ```bash
   git clone https://github.com/zerquix/qrfile-share.git
   cd qrfile-share
   ```

2. **(Opsional) Buat virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scriptsctivate     # Windows
   ```

3. **Install dependency:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan server lokal:**
   ```bash
   python app.py
   ```

5. **Akses di browser:**
   - http://localhost:8000
   - atau dari perangkat lain: `http://192.168.x.x:8000` (IP lokal)

---

## ðŸ—‚ï¸ Struktur Folder

```
qrfile-share/
â”œâ”€â”€ app.py                   # Backend utama (Flask)
â”œâ”€â”€ templates/
â”‚   â””â”€â”€ index.html           # Halaman upload & QR
â”œâ”€â”€ static/
â”‚   â””â”€â”€ qrcode.png           # Hasil QR Code
â”œâ”€â”€ uploads/                 # Folder penyimpanan file
â”œâ”€â”€ requirements.txt         # Daftar dependensi
â””â”€â”€ README.md                # Dokumentasi ini
```

---

## âš™ï¸ Pengaturan Opsional

- Durasi penyimpanan file bisa diubah di `app.py`:
  ```python
  FILE_EXPIRY_SECONDS = 600  # default: 10 menit
  ```
- Download otomatis hapus file: aktif secara default
- Untuk akses dari luar jaringan lokal, gunakan:
  ```bash
  ngrok http 8000
  ```

---

## ðŸ“¦ Teknologi Digunakan

- Python 3
- Flask
- qrcode (dengan Pillow)
- HTML + CSS sederhana (tanpa Bootstrap, tanpa JavaScript berat)

---

## ðŸ›¡ï¸ Lisensi

Proyek ini dirilis di bawah lisensi MIT. Silakan digunakan dan dimodifikasi.

---

## ðŸ¤ Kontribusi

Pull request terbuka untuk fitur seperti:
- CLI uploader
- Dockerfile
- Password download
- QR dengan expiry time embed

---

## ðŸ“¸ Demo

<img src="static/qrcode.png" alt="QR Code Example" width="200">

---

## ðŸ”— Repo & Kontak

GitHub: [github.com/zerquix/qrfile-share](https://github.com/zerquix/qrfile-share)  
Buka Issue jika ada pertanyaan, bug, atau saran pengembangan.

---

> Aplikasi ini dirancang untuk digunakan secara lokal tanpa ketergantungan pada cloud atau akun login.
