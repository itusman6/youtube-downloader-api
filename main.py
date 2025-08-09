from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Sample Netscape format cookies (you should replace with your actual cookies)
DEFAULT_COOKIES = """# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

.youtube.com	TRUE	/	FALSE	1758275410	_ga_R3HTL8G9BH	GS1.2.1723715410.1.0.1723715410.0.0.0
.youtube.com	TRUE	/	FALSE	1758275502	_ga	GA1.1.1184248780.1723715398
.youtube.com	TRUE	/	FALSE	1758275504	_ga_5RPMD1E2GM	GS1.1.1723715398.1.1.1723715504.58.0.0
.youtube.com	TRUE	/	TRUE	1789300775	PREF	tz=Asia.Karachi&f5=20000&f7=100
.youtube.com	TRUE	/	TRUE	1754742223	GPS	1
.youtube.com	TRUE	/	TRUE	1786276734	__Secure-1PSIDTS	sidts-CjUB5H03P5q2T5wdjIfPtTjX3VjVGmt2rbwG-80n-OiPBeXRWlkmJFgesFdE2XbVwBCKS8uLzxAA
.youtube.com	TRUE	/	TRUE	1786276734	__Secure-3PSIDTS	sidts-CjUB5H03P5q2T5wdjIfPtTjX3VjVGmt2rbwG-80n-OiPBeXRWlkmJFgesFdE2XbVwBCKS8uLzxAA
.youtube.com	TRUE	/	FALSE	1789300734	HSID	A3cYb0tm22ST6igqf
.youtube.com	TRUE	/	TRUE	1789300734	SSID	AWWnxExLE7d98LVa3
.youtube.com	TRUE	/	FALSE	1789300734	APISID	AOSrsWO-VTUhSxaB/AYK0kAdzirnw3Hx3W
.youtube.com	TRUE	/	TRUE	1789300734	SAPISID	aXJCEFbQvBGKnWee/AnznbBO-q6slyWfzp
.youtube.com	TRUE	/	TRUE	1789300734	__Secure-1PAPISID	aXJCEFbQvBGKnWee/AnznbBO-q6slyWfzp
.youtube.com	TRUE	/	TRUE	1789300734	__Secure-3PAPISID	aXJCEFbQvBGKnWee/AnznbBO-q6slyWfzp
.youtube.com	TRUE	/	FALSE	1789300734	SID	g.a0000Agl3xe3N-kjWhdoshtJzsWqVxB6JD3YSGQcnSsY4Q2Zga88iI8GAgrx_wGP-m3tArkLWQACgYKAUQSARUSFQHGX2MipC2pE4W15sB2mosbfgunrRoVAUF8yKq1ZeeiuPyPWHlk0pHg1yEB0076
.youtube.com	TRUE	/	TRUE	1789300734	__Secure-1PSID	g.a0000Agl3xe3N-kjWhdoshtJzsWqVxB6JD3YSGQcnSsY4Q2Zga88wX49Mr6NgkvYIObiT9UHrAACgYKAQASARUSFQHGX2Mi2YjpDuYnHHbLqGrCqpcKURoVAUF8yKoisaV3NizxUsk7W6WcyOx10076
.youtube.com	TRUE	/	TRUE	1789300734	__Secure-3PSID	g.a0000Agl3xe3N-kjWhdoshtJzsWqVxB6JD3YSGQcnSsY4Q2Zga88f8tz92mhh0pqR479-0EObgACgYKAUsSARUSFQHGX2Mi6s9XVM2usDNbEQQup29HoxoVAUF8yKpr-c8uuq8mdz6il6w3yHpB0076
.youtube.com	TRUE	/	TRUE	1789300735	LOGIN_INFO	AFmmF2swRQIgKmR04I6mEaI52A9lxFrux24ud3kmRenEH1sZDYxijPcCIQD_UtMItBE-RX7YAMDlX2x7QgLiCiJj98xa_62JRlpfJA:QUQ3MjNmeS1kTG56Sm5GUG9kTDRhMkFzTUk0ZEgtSE01eklDUTZ2UFozS0hrNUxEamdxaHdQVlBkMzN1QWRqMG9CcUpoQlpkNHRUMVk4c2x3WjFCRmtENVBwaktybFFvakNkOVNhX0hvcFhfSDkwNDFLWEkyTXRfS2tITXpuellRRDYwM0k1b0NYbHJLaGtKREFHUFdLTzlMbk54LXRnMXZn
.youtube.com	TRUE	/	FALSE	1786277172	SIDCC	AKEyXzX68JFmZ0_Zr_mKbkeMBVaQ07XYDVD30LorM_ycL9RJ7C4LW6jATQm2bKNN5Vg5J0XY
.youtube.com	TRUE	/	TRUE	1786277172	__Secure-1PSIDCC	AKEyXzV95SQxfH5vy9JikVxMNjkf1W1-uVnRuTmthlLXTqa-8mJSHaDjazVf14uW9lKhN-p1
.youtube.com	TRUE	/	TRUE	1786277172	__Secure-3PSIDCC	AKEyXzUHDXYEcEVwrgyMAK-ouerRQHKSR1to5Ki_zKmiemu9TxCEzIUHwcyhJR9u3Lz1905DdQ
.youtube.com	TRUE	/	TRUE	1770293170	VISITOR_INFO1_LIVE	48AwxKgm720
.youtube.com	TRUE	/	TRUE	1770293170	VISITOR_PRIVACY_METADATA	CgJQSxIEGgAgDg%3D%3D
.youtube.com	TRUE	/	TRUE	1770222114	__Secure-ROLLOUT_TOKEN	CK7Q--_rqPi6QBCI2PvmxdCMAxjmtOHDz_uOAw%3D%3D
.youtube.com	TRUE	/	TRUE	0	YSC	_Obs6UYCGV4

"""

@app.route('/')
def index():
    return "✅ YouTube Downloader API is Live!"

@app.route('/get_links')
def get_links():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing URL'}), 400
        
    # Use Vercel's writable /tmp directory
    temp_dir = '/tmp' if os.path.exists('/tmp') else tempfile.gettempdir()
    cookie_path = os.path.join(temp_dir, 'youtube_cookies.txt')
    
    # Create proper Netscape format cookies file if it doesn't exist
    if not os.path.exists(cookie_path):
        try:
            with open(cookie_path, 'w') as f:
                f.write(DEFAULT_COOKIES)
        except IOError as e:
            # If we can't write cookies file, proceed without it
            cookie_path = None        

    ydl_opts = {
        'quiet': True,
        'cookiefile': cookie_path,
        'skip_download': True,
        'forcejson': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []

            # Mapping of desired resolutions
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

                # Audio-only (MP3)
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    formats.append({
                        'format': 'mp3',
                        'ext': f.get('ext'),
                        'filesize_mb': round(f.get('filesize', 0) / 1024 / 1024, 2) if f.get('filesize') else None,
                        'url': f['url']
                    })
                    continue

                # MP4 or 3GP with audio and desired resolution
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
