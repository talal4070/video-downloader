# 🎥 Universal Video Downloader

A powerful web-based application to download videos from 1000+ websites with proxy support for bypassing restrictions.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- 🌐 **Universal Support**: Download from YouTube, Vimeo, Facebook, Instagram, Twitter, TikTok, Reddit, and 1000+ websites
- 📹 **Multiple Formats**: MP4, WebM, MKV, MP3, M4A, and more
- 🔒 **Proxy Support**: Bypass geo-restrictions and network blocks
- 📊 **Real-time Progress**: Track download progress with visual feedback
- 🎨 **Modern UI**: Clean, responsive interface
- ⚡ **Fast & Efficient**: Powered by yt-dlp

## 🚀 Quick Start

### Local Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/video-downloader.git
cd video-downloader
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

5. **Open browser**
Navigate to `http://localhost:5000`

## 📦 Project Structure

```
video-downloader/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore rules
├── README.md          # Documentation
├── Procfile           # Heroku deployment
├── runtime.txt        # Python version
├── templates/         # HTML templates
│   └── index.html
├── static/            # CSS, JS files
│   ├── style.css
│   └── script.js
└── downloads/         # Downloaded videos (gitignored)
    └── .gitkeep
```

## 🌐 Deployment Options

### Deploy to Heroku

1. **Install Heroku CLI**
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

2. **Login and create app**
```bash
heroku login
heroku create your-app-name
```

3. **Deploy**
```bash
git push heroku main
heroku open
```

### Deploy to Railway

1. Fork this repository
2. Go to [Railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your forked repository
5. Railway will auto-detect and deploy!

### Deploy to Render

1. Fork this repository
2. Go to [Render.com](https://render.com)
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### Deploy to PythonAnywhere

1. Create account at [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Open Bash console
3. Clone repository:
```bash
git clone https://github.com/yourusername/video-downloader.git
cd video-downloader
pip install -r requirements.txt
```
4. Configure web app in PythonAnywhere dashboard

## 🔧 Configuration

### Environment Variables

Create a `.env` file for local development:

```env
FLASK_ENV=development
PORT=5000
DOWNLOAD_DIR=downloads
```

For production, set these in your hosting platform.

### Proxy Configuration

The app supports HTTP/HTTPS/SOCKS proxies:

- **Format**: `http://proxy.example.com:8080`
- **With Auth**: Provide username and password in the UI
- **SOCKS**: `socks5://proxy.example.com:1080`

## 📖 Usage

1. **Enter Video URL**: Paste the URL of any video from supported websites
2. **Select Format**: Choose video format (MP4, WebM, etc.) or audio (MP3, M4A)
3. **Enable Proxy** (Optional): If the website is blocked, enable proxy and enter details
4. **Click Download**: Watch the progress and wait for completion!

## 🛠️ Supported Websites

This app supports 1000+ websites including:
- YouTube
- Vimeo
- Dailymotion
- Facebook
- Instagram
- Twitter/X
- TikTok
- Reddit
- Twitch
- And many more!

Full list: [yt-dlp supported sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

## ⚠️ Important Notes

- **FFmpeg Required**: For audio conversion (MP3, M4A), install FFmpeg
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org)
  - Linux: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`

- **Legal Notice**: Only download videos you have permission to download. Respect copyright laws.

- **Storage**: Downloaded videos are stored in the `downloads/` folder

- **Rate Limiting**: Some websites may rate-limit or block automated downloads

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - The powerful video downloader library
- [Flask](https://flask.palletsprojects.com/) - The web framework

## 📧 Contact

Talal Khan -[talalkhan1784@gmail.com](talalkhan1784@gmail.com)

Project Link: [https://github.com/talal4070/video-downloader](https://github.com/talal4070/video-downloader)

---

⭐ **Star this repository if you find it helpful!**
