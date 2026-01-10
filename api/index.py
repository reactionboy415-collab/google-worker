from flask import Flask, request, Response
import cloudscraper
import requests
import random
import time

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods=['POST', 'GET'])
def proxy_handler(path):
    if request.method == 'GET':
        return "Vercel Tunnel: ACTIVE ✅", 200

    # 1. Force Vercel to fetch a fresh IP for this specific thread
    try:
        # Shuffling providers forces the DNS to resolve differently
        providers = ['https://api.ipify.org', 'https://ifconfig.me/ip', 'https://icanhazip.com']
        scraped_ip = requests.get(f"{random.choice(providers)}?t={time.time()}", timeout=5).text.strip()
    except:
        scraped_ip = "Unknown"

    data = request.json
    target_url = data.get("url")
    
    # 2. Fresh Scraper Session for every single request
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'android', 'mobile': True}
    )
    
    try:
        # Bypass NoteGPT's internal edge cache with a timestamp
        final_url = f"{target_url}&v={time.time()}" if "?" in target_url else f"{target_url}?v={time.time()}"
        
        res = scraper.post(
            final_url, 
            json=data.get("payload"), 
            headers=data.get("headers"), 
            cookies=data.get("cookies"), 
            timeout=30
        )
        
        # 3. Build response with No-Persistence headers
        response = Response(res.text, status=res.status_code, content_type='application/json')
        response.headers['X-Vercel-IP'] = scraped_ip
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Connection'] = 'close'
        return response
    except Exception as e:
        return Response(f"Worker Error: {str(e)}", status=500)
