import os
import time
import threading
from flask import Flask, render_template, request, redirect, send_file, url_for, abort, jsonify
from werkzeug.utils import secure_filename
import qrcode

# === Konfigurasi ===
UPLOAD_FOLDER = 'uploads'
QR_CODE_PATH = os.path.join('static', 'qrcode.png')
FILE_EXPIRY_SECONDS = 600  # 10 menit
HOST = '0.0.0.0'
PORT = 8000

# === Inisialisasi Aplikasi ===
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Simpan file expiry dalam dict
file_registry = {}  # format: {filename: timestamp}

# Pastikan folder ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

# === ROUTE HALAMAN UTAMA ===
@app.route('/')
def index():
    return render_template('index.html')


# === ROUTE UPLOAD (AJAX) ===
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Simpan waktu unggah
    file_registry[filename] = time.time()

    # Generate QR Code pointing to direct download link
    download_url = url_for('download_file', filename=filename, _external=True)
    qr = qrcode.make(download_url)
    qr.save(QR_CODE_PATH)

    return jsonify({
        'filename': filename,
        'download_url': download_url,
        'qr_url': url_for('static', filename='qrcode.png', _external=True)
    })


# === ROUTE DOWNLOAD (langsung unduh) ===
@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Validasi file
    if not os.path.exists(filepath):
        abort(404)

    # Cek expiry
    uploaded_time = file_registry.get(filename)
    if uploaded_time and time.time() - uploaded_time > FILE_EXPIRY_SECONDS:
        try:
            os.remove(filepath)
        except:
            pass
        file_registry.pop(filename, None)
        abort(410, description="File expired")

    # Hapus setelah diunduh
    try:
        response = send_file(filepath, as_attachment=True)
        os.remove(filepath)
        file_registry.pop(filename, None)
        return response
    except Exception as e:
        abort(500, description=f"Download error: {str(e)}")


# === FUNGSI PENGHAPUS OTOMATIS ===
def cleanup_expired_files():
    while True:
        now = time.time()
        expired = [f for f, t in file_registry.items() if now - t > FILE_EXPIRY_SECONDS]
        for f in expired:
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, f))
            except:
                pass
            file_registry.pop(f, None)
        time.sleep(60)  # Cek setiap 1 menit


# === JALANKAN APP + CLEANUP THREAD ===
if __name__ == '__main__':
    cleanup_thread = threading.Thread(target=cleanup_expired_files, daemon=True)
    cleanup_thread.start()
    print(f"⚡ Running on http://localhost:{PORT} (or your local IP)")
    app.run(host=HOST, port=PORT, debug=False)
