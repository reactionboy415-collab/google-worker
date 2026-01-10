from flask import Flask, request, jsonify
import cloudscraper
import random
import uuid

app = Flask(__name__)

def get_ghost_headers():
    fake_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    return {
        'User-Agent': "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        'Accept': 'application/json, text/plain, */*',
        'X-Forwarded-For': fake_ip,
        'Origin': 'https://notegpt.io',
        'Referer': 'https://notegpt.io/ai-music-generator',
        'X-Requested-With': 'XMLHttpRequest'
    }

@app.route('/proxy', methods=['POST'])
def tunnel():
    try:
        data = request.json
        target_url = data.get("url")
        method = data.get("method", "POST")
        payload = data.get("payload")
        
        # Match your script: Generate a new anon ID for every music request
        anon_id = str(uuid.uuid4())
        cookies = {'anonymous_user_id': anon_id, 'is_accepted_terms': '1'}
        
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'android', 'mobile': True})
        headers = get_ghost_headers()

        if method == "POST":
            res = scraper.post(target_url, headers=headers, cookies=cookies, json=payload, timeout=25)
        else:
            res = scraper.get(target_url, headers=headers, cookies=cookies, timeout=25)

        # DEBUG: If not JSON, return the raw text to the Admin
        try:
            return jsonify(res.json())
        except:
            return jsonify({
                "code": 999, 
                "status_code": res.status_code, 
                "raw_html": res.text[:2000], # Capture the block page
                "msg": "Non-JSON response from NoteGPT"
            })
            
    except Exception as e:
        return jsonify({"code": 500, "error": str(e)})
