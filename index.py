from flask import Flask, request, jsonify
import cloudscraper
import uuid

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate_music():
    try:
        data = request.json
        topic = data.get("topic")
        lyrics = data.get("lyrics")
        
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'android'})
        # Fast session init
        scraper.get("https://notegpt.io/ai-music-generator", timeout=5)
        cookies = scraper.cookies.get_dict()
        cookies['anonymous_user_id'] = f"anon_{uuid.uuid4().hex}"
        
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36",
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://notegpt.io/ai-music-generator'
        }
        
        payload = {"prompt": f"Professional {topic}", "lyrics": lyrics, "duration": 0}
        res = scraper.post("https://notegpt.io/api/v2/music/generate", json=payload, cookies=cookies, headers=headers, timeout=10)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)})

@app.route('/status', methods=['GET'])
def get_status():
    try:
        cid = request.args.get("cid")
        scraper = cloudscraper.create_scraper()
        res = scraper.get(f"https://notegpt.io/api/v2/music/status?conversation_id={cid}", timeout=5)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)})
