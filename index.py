from flask import Flask, request, jsonify
import cloudscraper
import random

app = Flask(__name__)

@app.route('/proxy', methods=['POST'])
def tunnel():
    try:
        data = request.json
        target_url = data.get("url")
        method = data.get("method", "POST")
        payload = data.get("payload")
        
        # Ghost Identity logic from your script
        fake_ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            'X-Forwarded-For': fake_ip,
            'Origin': 'https://notegpt.io',
            'Referer': 'https://notegpt.io/ai-music-generator',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        scraper = cloudscraper.create_scraper()
        if method == "POST":
            res = scraper.post(target_url, headers=headers, json=payload, timeout=15)
        else:
            res = scraper.get(target_url, headers=headers, timeout=15)
            
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e), "code": 500})
