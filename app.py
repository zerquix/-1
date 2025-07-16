import os
import time
import threading
from flask import Flask, request, send_file, render_template, url_for, redirect, abort, jsonify
from werkzeug.utils import secure_filename
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
QR_FOLDER = 'static/qr'
FILE_EXPIRY_SECONDS = 600  # 10 minutes

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

file_registry = {}

def generate_unique_filename(original_filename):
    """Generate unique filename to prevent conflicts"""
    name, ext = os.path.splitext(original_filename)
    unique_id = str(uuid.uuid4())[:8]
    return f"{name}_{unique_id}{ext}"

def create_qr_code(data, filename):
    """Create a styled QR code"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create QR with rounded corners
    img = qr.make_image(
        fill_color="black",
        back_color="white",
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer()
    )
    
    qr_path = os.path.join(QR_FOLDER, f"{filename}.png")
    img.save(qr_path)
    return qr_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files.get('file')
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Generate unique filename
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename)
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(filepath)
        
        # Register file with metadata
        file_registry[unique_filename] = {
            'original_name': original_filename,
            'created_at': time.time(),
            'size': os.path.getsize(filepath)
        }
        
        # Generate download URL and QR code
        download_url = url_for('download_file', filename=unique_filename, _external=True)
        qr_path = create_qr_code(download_url, unique_filename)
        
        return jsonify({
            'success': True,
            'qr_url': url_for('static', filename=f'qr/{unique_filename}.png'),
            'download_url': download_url,
            'filename': original_filename,
            'size': file_registry[unique_filename]['size']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    # Check if file exists
    if not os.path.exists(filepath):
        abort(404)
    
    # Check if file is registered and not expired
    if filename not in file_registry:
        abort(404)
    
    created_at = file_registry[filename]['created_at']
    if time.time() - created_at > FILE_EXPIRY_SECONDS:
        cleanup_file(filename)
        abort(410)  # Gone
    
    try:
        original_name = file_registry[filename]['original_name']
        response = send_file(filepath, as_attachment=True, download_name=original_name)
        
        # Clean up after successful download
        cleanup_file(filename)
        return response
        
    except Exception as e:
        abort(500)

def cleanup_file(filename):
    """Clean up file and its QR code"""
    try:
        # Remove file
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Remove QR code
        qr_path = os.path.join(QR_FOLDER, f"{filename}.png")
        if os.path.exists(qr_path):
            os.remove(qr_path)
        
        # Remove from registry
        file_registry.pop(filename, None)
        
    except Exception:
        pass

def auto_cleanup():
    """Background cleanup task"""
    while True:
        try:
            now = time.time()
            expired_files = []
            
            for filename, metadata in file_registry.items():
                if now - metadata['created_at'] > FILE_EXPIRY_SECONDS:
                    expired_files.append(filename)
            
            for filename in expired_files:
                cleanup_file(filename)
                
        except Exception:
            pass
        
        time.sleep(60)  # Check every minute

@app.route('/status')
def status():
    """Get server status"""
    return jsonify({
        'active_files': len(file_registry),
        'uptime': time.time()
    })

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large (max 50MB)'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'File not found'}), 404

@app.errorhandler(410)
def gone(e):
    return jsonify({'error': 'File expired'}), 410

if __name__ == '__main__':
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=auto_cleanup, daemon=True)
    cleanup_thread.start()
    
    # Run app
    app.run(host='0.0.0.0', port=8000, debug=False)
