import os
import time
import threading
from flask import Flask, render_template, request, send_file, url_for, jsonify, abort
from werkzeug.utils import secure_filename
import qrcode

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
QR_PATH = os.path.join('static', 'qrcode.png')
FILE_EXPIRY_SECONDS = 600  # 10 menit

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

file_registry = {}  # Simpan waktu unggah per file

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    file_registry[filename] = time.time()

    # Generate QR Code
    download_url = url_for('download_file', filename=filename, _external=True)
    qr = qrcode.make(download_url)
    qr.save(QR_PATH)

    return jsonify({
        'download_url': download_url,
        'qr_url': url_for('static', filename='qrcode.png')
    })

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        abort(404)

    upload_time = file_registry.get(filename)
    if upload_time and time.time() - upload_time > FILE_EXPIRY_SECONDS:
        os.remove(filepath)
        file_registry.pop(filename, None)
        abort(410, "File expired")

    # Send file, then delete
    try:
        response = send_file(filepath, as_attachment=True)
        os.remove(filepath)
        file_registry.pop(filename, None)
        return response
    except Exception:
        abort(500, "Download failed")

def cleanup_expired_files():
    while True:
        now = time.time()
        for filename in list(file_registry.keys()):
            if now - file_registry[filename] > FILE_EXPIRY_SECONDS:
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    os.remove(path)
                except:
                    pass
                file_registry.pop(filename, None)
        time.sleep(60)

if __name__ == '__main__':
    threading.Thread(target=cleanup_expired_files, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)
