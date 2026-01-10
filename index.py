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
        scraper.get("https://notegpt.io/ai-music-generator", timeout=5)
        
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36",
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://notegpt.io/ai-music-generator'
        }
        
        payload = {"prompt": f"Professional {topic}", "lyrics": lyrics, "duration": 0}
        # Attempt generation
        res = scraper.post("https://notegpt.io/api/v2/music/generate", json=payload, timeout=10)
        
        # Return full response for debugging
        return jsonify({
            "status_code": res.status_code,
            "raw_response": res.text,
            "json": res.json() if res.status_code == 200 else {}
        })
    except Exception as e:
        return jsonify({"status_code": 500, "error": str(e)})

@app.route('/status', methods=['GET'])
def get_status():
    cid = request.args.get("cid")
    scraper = cloudscraper.create_scraper()
    res = scraper.get(f"https://notegpt.io/api/v2/music/status?conversation_id={cid}", timeout=5)
    return jsonify(res.json())
