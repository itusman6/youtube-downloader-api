from flask import Flask, request, jsonify
import yt_dlp
import os
import tempfile
import browser_cookie3

app = Flask(__name__)

def get_temp_cookie_file():
    """Extract cookies from Chrome and save to a temporary file"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_cookie_file:
        cookie_path = temp_cookie_file.name

    cookies = browser_cookie3.chrome()  # Chrome se cookies le
    cookie_str = ""
    for cookie in cookies:
        cookie_str += f"{cookie.domain}\t{'TRUE' if cookie.domain.startswith('.') else 'FALSE'}\t{cookie.path}\t{'TRUE' if cookie.secure else 'FALSE'}\t{cookie.expires}\t{cookie.name}\t{cookie.value}\n"

    with open(cookie_path, "w", encoding="utf-8") as f:
        f.write(cookie_str)

    return cookie_path

@app.route('/')
def index():
    return "✅ YouTube Downloader API is Live!"

@app.route('/get_links')
def get_links():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing URL'}), 400

    # Get cookies temp file
    cookie_path = get_temp_cookie_file()

    ydl_opts = {
        'quiet': True,
        'cookiefile': cookie_path,  # temp cookie file use karein
        'skip_download': True,
        'forcejson': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []

            desired_resolutions = {
                'mp3': 'audio_only',
                '144p': ['144p', 'tiny'],
                '240p': ['240p'],
                '360p': ['360p'],
                '480p': ['480p'],
                '720p': ['720p', 'hd720'],
                '1080p': ['1080p', 'hd1080'],
                '1440p': ['1440p', 'hd1440'],
                '2160p': ['2160p', 'hd2160'],
            }

            for f in info.get('formats', []):
                if not f.get('url'):
                    continue

                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    formats.append({
                        'format': 'mp3',
                        'ext': f.get('ext'),
                        'filesize_mb': round(f.get('filesize', 0) / 1024 / 1024, 2) if f.get('filesize') else None,
                        'url': f['url']
                    })
                    continue

                if f.get('acodec') != 'none' and f.get('vcodec') != 'none':
                    note = f.get('format_note') or f.get('height') or ""
                    for res, keywords in desired_resolutions.items():
                        if res == 'mp3':
                            continue
                        if any(str(note).lower().find(k) != -1 for k in keywords):
                            formats.append({
                                'format': res,
                                'ext': f.get('ext'),
                                'filesize_mb': round(f.get('filesize', 0) / 1024 / 1024, 2) if f.get('filesize') else None,
                                'url': f['url']
                            })
                            break

            return jsonify({
                'title': info.get('title'),
                'url': info.get('webpage_url'),
                'formats': formats
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(cookie_path):
            os.remove(cookie_path)  # clean up temp file

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
