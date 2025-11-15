from flask import Flask, render_template, request, jsonify, send_from_directory
import yt_dlp
import os
import threading
import time
import uuid
from pathlib import Path

app = Flask(__name__)

# Configuration
DOWNLOAD_DIR = os.environ.get('DOWNLOAD_DIR', 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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
            'message': 'Download completed!'
        }

def download_video(url, format_choice, download_id, proxy_config=None):
    """Download video in a separate thread"""
    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
            'quiet': True,
            'no_warnings': True,
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

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        download_status[download_id] = {
            'status': 'completed',
            'progress': 100,
            'message': 'Download completed successfully!'
        }

    except Exception as e:
        download_status[download_id] = {
            'status': 'error',
            'error': str(e)
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

        return jsonify({'success': True, 'download_id': download_id})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/progress/<download_id>')
def progress(download_id):
    if download_id in download_status:
        return jsonify(download_status[download_id])
    else:
        return jsonify({'status': 'not_found'})

@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
