import os
import time
from flask import Flask, request, render_template, send_file, abort, url_for
from werkzeug.utils import secure_filename
import qrcode

# Konfigurasi
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
QR_CODE_PATH = os.path.join(STATIC_FOLDER, 'qrcode.png')
FILE_EXPIRY_SECONDS = 600  # 10 menit
HOST = '0.0.0.0'
PORT = 8000

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Pastikan direktori ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# Halaman utama
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

        # URL akan langsung memicu download
        file_url = url_for('download_file', filename=filename, _external=True)

        # Buat QR Code
        qr = qrcode.make(file_url)
        qr.save(QR_CODE_PATH)

    return render_template('index.html', file_url=file_url, filename=filename)


@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(path):
        return abort(404, description="File tidak ditemukan atau sudah dihapus.")

    # Unduh dan hapus file setelah diakses
    response = send_file(path, as_attachment=True)
    os.remove(path)
    if os.path.exists(QR_CODE_PATH):
        os.remove(QR_CODE_PATH)
    return response


# Opsional: Auto-hapus file kadaluarsa
def cleanup_uploads():
    now = time.time()
    for fname in os.listdir(UPLOAD_FOLDER):
        fpath = os.path.join(UPLOAD_FOLDER, fname)
        if os.path.isfile(fpath) and (now - os.path.getmtime(fpath)) > FILE_EXPIRY_SECONDS:
            os.remove(fpath)

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)
