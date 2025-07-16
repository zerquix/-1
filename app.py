import os
import time
import threading
from flask import Flask, request, send_from_directory, render_template, redirect, url_for, abort
import qrcode
from werkzeug.utils import secure_filename

# Konfigurasi dasar
UPLOAD_FOLDER = 'uploads'
QR_PATH = 'static/qrcode.png'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar', 'mp4', 'mp3', 'apk', 'docx'])
FILE_EXPIRY_SECONDS = 600  # 10 menit
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Pastikan direktori ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)


# Fungsi pembantu
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_old_files():
    while True:
        now = time.time()
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath) and now - os.path.getmtime(filepath) > FILE_EXPIRY_SECONDS:
                try:
                    os.remove(filepath)
                except Exception:
                    pass
        time.sleep(600)  # Setiap 10 menit


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Cegah overwrite
            counter = 1
            base, ext = os.path.splitext(filename)
            while os.path.exists(filepath):
                filename = f"{base}_{counter}{ext}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                counter += 1

            file.save(filepath)

            download_url = request.url_root + 'download/' + filename
            generate_qr_code(download_url)

            return render_template('index.html', filename=filename, qr_url=url_for('static', filename='qrcode.png'), download_url=download_url)

    return render_template('index.html')


@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.isfile(filepath):
        abort(404)

    response = send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

    # Auto-delete setelah 1 download (opsional tapi diaktifkan di sini)
    try:
        os.remove(filepath)
    except Exception:
        pass

    return response


def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(QR_PATH)


# Jalankan thread cleanup
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
