from flask import Flask, request, Response
import cloudscraper
import requests
import time
import random

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods=['POST', 'GET'])
def proxy_handler(path):
    if request.method == 'GET': return "Ghost Tunnel: Active", 200
    
    data = request.json
    # Generate a random Chrome version to bypass fingerprinting
    chrome_v = f"{random.randint(110, 122)}.0.{random.randint(1000, 9999)}.{random.randint(1, 150)}"
    user_agent = f"Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_v} Mobile Safari/537.36"
    
    headers = data.get("headers", {})
    headers['User-Agent'] = user_agent
    
    try:
        scraped_ip = requests.get(f"https://api.ipify.org?t={time.time()}", timeout=5).text.strip()
    except: scraped_ip = "Unknown"

    scraper = cloudscraper.create_scraper()
    try:
        res = scraper.post(data['url'], json=data['payload'], headers=headers, cookies=data['cookies'], timeout=30)
        resp = Response(res.text, status=res.status_code, content_type='application/json')
        resp.headers['X-Vercel-IP'] = scraped_ip
        return resp
    except Exception as e:
        return Response(str(e), status=500)
