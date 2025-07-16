import os
import time
import threading
from flask import Flask, request, send_file, jsonify, render_template, url_for, abort
from werkzeug.utils import secure_filename
import qrcode

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
QR_IMAGE = os.path.join('static', 'qrcode.png')
FILE_EXPIRY_SECONDS = 600  # 10 menit

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

file_registry = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    file_registry[filename] = time.time()

    download_url = url_for('download_file', filename=filename, _external=True)
    qr = qrcode.make(download_url)
    qr.save(QR_IMAGE)

    return jsonify({
        'qr_url': url_for('static', filename='qrcode.png') + f'?t={int(time.time())}',
        'download_url': download_url
    })

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(filepath):
        abort(404)

    created = file_registry.get(filename)
    if created and time.time() - created > FILE_EXPIRY_SECONDS:
        os.remove(filepath)
        file_registry.pop(filename, None)
        abort(410)

    try:
        response = send_file(filepath, as_attachment=True)
        os.remove(filepath)
        file_registry.pop(filename, None)
        return response
    except:
        abort(500)

def auto_cleanup():
    while True:
        now = time.time()
        for filename in list(file_registry.keys()):
            created = file_registry[filename]
            if now - created > FILE_EXPIRY_SECONDS:
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, filename))
                except:
                    pass
                file_registry.pop(filename, None)
        time.sleep(60)

if __name__ == '__main__':
    threading.Thread(target=auto_cleanup, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)
