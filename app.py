import os
import time
from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
import qrcode

# Konfigurasi
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
QR_CODE_PATH = os.path.join(STATIC_FOLDER, 'qrcode.png')
FILE_EXPIRY_SECONDS = 600  # 10 menit
HOST = '0.0.0.0'
PORT = 8000

# Setup Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Pastikan folder ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    file_url = None
    filename = None

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template("index.html", error="Tidak ada file ditemukan.")

        file = request.files['file']
        if file.filename == '':
            return render_template("index.html", error="Nama file kosong.")

        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        # Buat URL download lokal
        file_url = f"http://{request.host}/uploads/{filename}"

        # Buat QR Code
        qr = qrcode.make(file_url)
        qr.save(QR_CODE_PATH)

    return render_template('index.html', file_url=file_url, filename=filename)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(path):
        return "File tidak ditemukan atau sudah dihapus.", 404

    # Hapus setelah 1 download (opsional)
    response = send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    os.remove(path)
    if os.path.exists(QR_CODE_PATH):
        os.remove(QR_CODE_PATH)
    return response


# Auto-hapus file expired (optional bisa dijadikan background task)
def cleanup_uploads():
    now = time.time()
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(filepath) and now - os.path.getmtime(filepath) > FILE_EXPIRY_SECONDS:
            os.remove(filepath)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)
