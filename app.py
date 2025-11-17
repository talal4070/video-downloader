from flask import Flask, render_template, request, jsonify, send_from_directory
import yt_dlp
import os
import threading
import time
import uuid
from pathlib import Path
import tempfile

app = Flask(__name__)

# Railway-compatible configuration
if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_STATIC_URL'):
    # Use temp directory on Railway (ephemeral storage)
    DOWNLOAD_DIR = tempfile.gettempdir()
    print("🚀 Running on Railway - using temporary storage")
else:
    # Local development
    DOWNLOAD_DIR = os.environ.get('DOWNLOAD_DIR', 'downloads')
    print("💻 Running locally - using downloads folder")

# Ensure download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
print(f"📁 Download directory: {DOWNLOAD_DIR}")

# Store download progress
download_status = {}

def progress_hook(d, download_id):
    """Callback function for download progress"""
    if d['status'] == 'downloading':
        if 'total_bytes' in d and d['total_bytes'] > 0:
            percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
            download_status[download_id] = {
                'status': 'downloading',
                'progress': round(percent, 1),
                'message': f"Downloading... {d['downloaded_bytes']/(1024*1024):.1f}MB / {d['total_bytes']/(1024*1024):.1f}MB"
            }
        else:
            download_status[download_id] = {
                'status': 'downloading',
                'progress': 0,
                'message': 'Downloading...'
            }
    elif d['status'] == 'finished':
        download_status[download_id] = {
            'status': 'completed',
            'progress': 100,
            'message': 'Download completed! Processing file...'
        }
    elif d['status'] == 'error':
        download_status[download_id] = {
            'status': 'error',
            'error': 'Download failed - please check the URL and try again'
        }

def cleanup_old_files():
    """Clean up files older than 1 hour"""
    try:
        current_time = time.time()
        for filename in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            if os.path.isfile(file_path):
                # Remove files older than 1 hour
                if current_time - os.path.getctime(file_path) > 3600:
                    os.remove(file_path)
                    print(f"🧹 Cleaned up old file: {filename}")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")

def download_video(url, format_choice, download_id, proxy_config=None):
    """Download video in a separate thread"""
    try:
        # Clean up old files before starting new download
        cleanup_old_files()
        
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title).100s.%(ext)s'),
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
            'quiet': False,  # Set to True for production
            'no_warnings': False,
            'ignoreerrors': True,
        }

        # Format selection
        if format_choice == 'best':
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        elif format_choice == 'mp3':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif format_choice == 'm4a':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }]
        elif format_choice == 'worst':
            ydl_opts['format'] = 'worst'
        else:
            ydl_opts['format'] = f'bestvideo[ext={format_choice}]+bestaudio/best[ext={format_choice}]/best'

        # Proxy configuration
        if proxy_config and proxy_config.get('use_proxy'):
            proxy_url = proxy_config.get('proxy_url')
            if proxy_url:
                if proxy_config.get('proxy_user') and proxy_config.get('proxy_pass'):
                    from urllib.parse import urlparse, urlunparse
                    parsed = urlparse(proxy_url)
                    netloc = f"{proxy_config['proxy_user']}:{proxy_config['proxy_pass']}@{parsed.hostname}"
                    if parsed.port:
                        netloc += f":{parsed.port}"
                    proxy_url = urlunparse((parsed.scheme, netloc, parsed.path, '', '', ''))
                
                ydl_opts['proxy'] = proxy_url

        download_status[download_id] = {
            'status': 'downloading',
            'progress': 0,
            'message': 'Initializing download...'
        }

        print(f"📥 Starting download: {url}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Update status with filename
            download_status[download_id] = {
                'status': 'completed',
                'progress': 100,
                'message': 'Download completed successfully!',
                'filename': os.path.basename(filename)
            }

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Download error: {error_msg}")
        download_status[download_id] = {
            'status': 'error',
            'error': f'Download failed: {error_msg}'
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.json
        url = data.get('url')
        format_choice = data.get('format', 'best')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL is required'})

        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            return jsonify({'success': False, 'error': 'Invalid URL format'})

        download_id = str(uuid.uuid4())

        proxy_config = None
        if data.get('use_proxy'):
            proxy_config = {
                'use_proxy': True,
                'proxy_url': data.get('proxy_url'),
                'proxy_user': data.get('proxy_user'),
                'proxy_pass': data.get('proxy_pass')
            }

        thread = threading.Thread(
            target=download_video,
            args=(url, format_choice, download_id, proxy_config)
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            'success': True, 
            'download_id': download_id,
            'message': 'Download started successfully!'
        })

    except Exception as e:
        print(f"❌ Route error: {e}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'})

@app.route('/progress/<download_id>')
def progress(download_id):
    try:
        if download_id in download_status:
            return jsonify(download_status[download_id])
        else:
            return jsonify({'status': 'not_found', 'message': 'Download ID not found'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/downloads/<path:filename>')
def download_file(filename):
    try:
        # Security check - prevent directory traversal
        if '..' in filename or filename.startswith('/'):
            return "Invalid filename", 400
            
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        if not os.path.exists(file_path):
            return "File not found", 404
            
        return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)
    except Exception as e:
        print(f"❌ File download error: {e}")
        return "Error downloading file", 500

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'download_dir': DOWNLOAD_DIR,
        'files_count': len(os.listdir(DOWNLOAD_DIR)) if os.path.exists(DOWNLOAD_DIR) else 0
    })

@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    """Manual cleanup endpoint"""
    try:
        cleanup_old_files()
        return jsonify({'success': True, 'message': 'Cleanup completed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Flask app on port {port}")
    print(f"📁 Download directory: {DOWNLOAD_DIR}")
    app.run(debug=False, host='0.0.0.0', port=port)
