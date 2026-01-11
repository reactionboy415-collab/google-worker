from flask import Flask, request, Response
import cloudscraper
import requests
import time
import os

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods=['POST', 'GET'])
def proxy_handler(path):
    if request.method == 'GET':
        return "Tunnel Active ✅", 200
    
    # Get current Vercel Region
    region = os.environ.get('VERCEL_REGION', 'unknown')
    
    # Force fresh IP check by killing local cache
    try:
        scraped_ip = requests.get(f"https://api.ipify.org?t={time.time()}", timeout=5).text.strip()
    except:
        scraped_ip = "Unknown"

    data = request.json
    scraper = cloudscraper.create_scraper()
    
    try:
        res = scraper.post(
            data['url'], 
            json=data['payload'], 
            headers=data['headers'], 
            cookies=data['cookies'], 
            timeout=30
        )
        
        resp = Response(res.text, status=res.status_code, content_type='application/json')
        # Pass networking info back to the bot
        resp.headers['X-Vercel-IP'] = scraped_ip
        resp.headers['X-Vercel-Region'] = region
        return resp
    except Exception as e:
        return Response(str(e), status=500)
