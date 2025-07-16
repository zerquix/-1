document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const uploadForm = document.getElementById('uploadForm');
    const uploadBtn = document.getElementById('uploadBtn');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const error = document.getElementById('error');
    const qrCode = document.getElementById('qrCode');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const downloadLink = document.getElementById('downloadLink');
    const newFileBtn = document.getElementById('newFileBtn');
    const retryBtn = document.getElementById('retryBtn');
    const errorMessage = document.getElementById('errorMessage');

    let selectedFile = null;

    // File input change handler
    fileInput.addEventListener('change', function(e) {
        handleFileSelect(e.target.files[0]);
    });

    // Upload area click handler
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });

    // Drag and drop handlers
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', function() {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    // Form submit handler
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (selectedFile) {
            uploadFile(selectedFile);
        }
    });

    // New file button handler
    newFileBtn.addEventListener('click', function() {
        resetForm();
    });

    // Retry button handler
    retryBtn.addEventListener('click', function() {
        hideAllSections();
        showUploadForm();
    });

    function handleFileSelect(file) {
        if (!file) return;

        // Check file size (50MB limit)
        if (file.size > 50 * 1024 * 1024) {
            showError('File terlalu besar! Maksimal 50MB.');
            return;
        }

        selectedFile = file;
        updateUploadText(file.name);
        uploadBtn.disabled = false;
    }

    function updateUploadText(filename) {
        const uploadText = uploadArea.querySelector('.upload-text');
        const uploadSubtext = uploadArea.querySelector('.upload-subtext');
        
        uploadText.textContent = filename;
        uploadSubtext.textContent = formatFileSize(selectedFile.size);
    }

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        hideAllSections();
        loading.classList.remove('hidden');

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loading.classList.add('hidden');
            
            if (data.success) {
                showResult(data);
            } else {
                showError(data.error || 'Terjadi kesalahan saat mengunggah file.');
            }
        })
        .catch(err => {
            loading.classList.add('hidden');
            showError('Koneksi gagal. Periksa koneksi internet Anda.');
        });
    }

    function showResult(data) {
        qrCode.src = data.qr_url;
        fileName.textContent = data.filename;
        fileSize.textContent = formatFileSize(data.size);
        downloadLink.href = data.download_url;
        
        result.classList.remove('hidden');
    }

    function showError(message) {
        errorMessage.textContent = message;
        error.classList.remove('hidden');
    }

    function hideAllSections() {
        loading.classList.add('hidden');
        result.classList.add('hidden');
        error.classList.add('hidden');
    }

    function showUploadForm() {
        resetForm();
    }

    function resetForm() {
        selectedFile = null;
        fileInput.value = '';
        uploadBtn.disabled = true;
        
        const uploadText = uploadArea.querySelector('.upload-text');
        const uploadSubtext = uploadArea.querySelector('.upload-subtext');
        
        uploadText.textContent = 'Pilih file atau drag & drop';
        uploadSubtext.textContent = 'Maksimal 50MB';
        
        hideAllSections();
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Prevent default drag behaviors on document
    document.addEventListener('dragover', function(e) {
        e.preventDefault();
    });

    document.addEventListener('drop', function(e) {
        e.preventDefault();
    });
});
