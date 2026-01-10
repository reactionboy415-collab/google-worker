from flask import Flask, request, Response
import cloudscraper
import requests
import time

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods=['POST', 'GET'])
def catch_all(path):
    if request.method == 'GET':
        return "Vercel Tunnel: ACTIVE ✅", 200

    data = request.json
    target_url = data.get("url")
    
    # Force Vercel to drop the current connection and pick a new one
    try:
        # Using a timestamped request to bypass Vercel internal routing cache
        scraped_ip = requests.get(f'https://api.ipify.org?t={time.time()}', timeout=5).text.strip()
    except:
        scraped_ip = "Unknown"

    scraper = cloudscraper.create_scraper()
    
    try:
        res = scraper.post(
            target_url, 
            json=data.get("payload"), 
            headers=data.get("headers"), 
            cookies=data.get("cookies"), 
            timeout=25
        )
        
        response = Response(res.text, status=res.status_code, content_type=res.headers.get('Content-Type'))
        # Attach the unique IP found for this specific execution
        response.headers['X-Vercel-IP'] = scraped_ip
        # Prevent Vercel from caching this path
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    except Exception as e:
        return Response(f"Worker Error: {str(e)}", status=500)
