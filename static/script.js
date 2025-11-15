const form = document.getElementById('downloadForm');
const downloadBtn = document.getElementById('downloadBtn');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const status = document.getElementById('status');
const errorDiv = document.getElementById('error');
const successDiv = document.getElementById('success');
const useProxyCheckbox = document.getElementById('useProxy');
const proxyInputs = document.getElementById('proxyInputs');

useProxyCheckbox.addEventListener('change', function() {
    proxyInputs.classList.toggle('active', this.checked);
});

form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    errorDiv.classList.remove('active');
    successDiv.classList.remove('active');
    progressContainer.classList.add('active');
    downloadBtn.disabled = true;
    progressFill.style.width = '0%';
    progressFill.textContent = '0%';
    status.textContent = 'Starting download...';

    const formData = new FormData(form);
    const data = {
        url: formData.get('url'),
        format: formData.get('format'),
        use_proxy: formData.get('useProxy') === 'on',
        proxy_url: formData.get('proxyUrl'),
        proxy_user: formData.get('proxyUser'),
        proxy_pass: formData.get('proxyPass')
    };

    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            checkProgress(result.download_id);
        } else {
            showError(result.error);
            downloadBtn.disabled = false;
        }
    } catch (error) {
        showError('Network error: ' + error.message);
        downloadBtn.disabled = false;
    }
});

function checkProgress(downloadId) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/progress/${downloadId}`);
            const data = await response.json();

            if (data.status === 'downloading') {
                const percent = data.progress || 0;
                progressFill.style.width = percent + '%';
                progressFill.textContent = percent + '%';
                status.textContent = data.message || 'Downloading...';
            } else if (data.status === 'completed') {
                clearInterval(interval);
                progressFill.style.width = '100%';
                progressFill.textContent = '100%';
                status.textContent = 'Download completed!';
                showSuccess('Video downloaded successfully! Check your downloads folder.');
                downloadBtn.disabled = false;
            } else if (data.status === 'error') {
                clearInterval(interval);
                showError(data.error);
                downloadBtn.disabled = false;
            }
        } catch (error) {
            clearInterval(interval);
            showError('Error checking progress');
            downloadBtn.disabled = false;
        }
    }, 500);
}

function showError(message) {
    errorDiv.textContent = '❌ ' + message;
    errorDiv.classList.add('active');
    progressContainer.classList.remove('active');
}

function showSuccess(message) {
    successDiv.textContent = '✅ ' + message;
    successDiv.classList.add('active');
}
