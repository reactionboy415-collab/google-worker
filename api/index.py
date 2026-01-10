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
        return "Tunnel: ACTIVE ✅", 200

    # 1. TRIPLE-IP CHECK (Forces DNS/Route change)
    try:
        urls = ['https://api.ipify.org', 'https://ifconfig.me/ip', 'https://icanhazip.com']
        # Adding a random timestamp (?t=) kills Vercel edge caching
        scraped_ip = requests.get(f"{random.choice(urls)}?t={time.time()}", timeout=5).text.strip()
    except:
        scraped_ip = "Unknown"

    data = request.json
    target_url = data.get("url")
    
    # 2. BRAND NEW SESSION
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'android','mobile': True})
    
    try:
        # 3. Add Cache-Buster to target URL
        final_url = f"{target_url}&v={time.time()}" if "?" in target_url else f"{target_url}?v={time.time()}"
        
        res = scraper.post(
            final_url, 
            json=data.get("payload"), 
            headers=data.get("headers"), 
            cookies=data.get("cookies"), 
            timeout=30
        )
        
        # 4. Return response with X-Vercel-IP and NO-CACHE headers
        response = Response(res.text, status=res.status_code, content_type='application/json')
        response.headers['X-Vercel-IP'] = scraped_ip
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Connection'] = 'close'
        return response
    except Exception as e:
        return Response(str(e), status=500)
