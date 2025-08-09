import os
import base64
import tempfile
import yt_dlp
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/get_links')
def get_links():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing URL'}), 400

    cookie_data_b64 = os.environ.get("YT_COOKIES_BASE64")
    cookie_path = None

    if cookie_data_b64:
        cookie_bytes = base64.b64decode(cookie_data_b64)
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp:
            tmp.write(cookie_bytes)
            cookie_path = tmp.name

    ydl_opts = {
        'quiet': True,
        'cookiefile': cookie_path if cookie_path else None,
        'skip_download': True,
        'forcejson': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
