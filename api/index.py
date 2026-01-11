from flask import Flask, request, Response
import cloudscraper
import requests
import time
import random
import os

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods=['POST', 'GET'])
def ghost_proxy(path):
    if request.method == 'GET': 
        return "Studio Worker Active ✅", 200
    
    # Get the current Vercel Region for Admin reporting
    region = os.environ.get('VERCEL_REGION', 'global')
    
    data = request.json
    # Generate random Chrome versions to bypass fingerprinting
    chrome_v = f"{random.randint(110, 126)}.0.{random.randint(1000, 9999)}.{random.randint(1, 150)}"
    headers = data.get("headers", {})
    headers['User-Agent'] = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_v} Safari/537.36"
    
    try:
        # Check current exit IP
        scraped_ip = requests.get(f"https://api.ipify.org?t={time.time()}", timeout=5).text.strip()
    except: 
        scraped_ip = "Unknown"

    scraper = cloudscraper.create_scraper()
    try:
        res = scraper.post(data['url'], json=data['payload'], headers=headers, cookies=data['cookies'], timeout=30)
        resp = Response(res.text, status=res.status_code, content_type='application/json')
        
        # Pass technical data back to the bot headers
        resp.headers['X-Studio-Addr'] = scraped_ip
        resp.headers['X-Studio-Reg'] = region
        return resp
    except Exception as e:
        return Response(str(e), status=500)
      
