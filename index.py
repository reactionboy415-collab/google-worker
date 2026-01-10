from flask import Flask, request, jsonify
import cloudscraper
import random
import uuid

app = Flask(__name__)

def get_ghost_headers():
    # Exact logic from your local script
    fake_ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
    return {
        'User-Agent': "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        'Accept': 'application/json, text/plain, */*',
        'X-Forwarded-For': fake_ip,
        'Origin': 'https://notegpt.io',
        'Referer': 'https://notegpt.io/ai-music-generator',
        'X-Requested-With': 'XMLHttpRequest'
    }

@app.route('/proxy', methods=['POST'])
def fire_engine():
    try:
        data = request.json
        target_url = data.get("url")
        method = data.get("method", "GET")
        payload = data.get("payload")
        cookies = data.get("cookies", {})
        
        # Initialize Scraper per request (Fresh Session)
        scraper = cloudscraper.create_scraper()
        headers = get_ghost_headers()
        
        if method == "POST":
            res = scraper.post(target_url, json=payload, headers=headers, cookies=cookies, timeout=25)
        else:
            res = scraper.get(target_url, headers=headers, cookies=cookies, timeout=25)
            
        # Return exact JSON from NoteGPT
        return jsonify(res.json())
        
    except Exception as e:
        # If Cloudflare blocks it, we catch it here
        return jsonify({"code": 500, "error": str(e)})
