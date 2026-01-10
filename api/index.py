from flask import Flask, request, Response
import cloudscraper
import requests
import time

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods=['POST', 'GET'])
def proxy_handler(path):
    if request.method == 'GET':
        return "Vercel Tunnel: ACTIVE ✅", 200

    # 1. Force Vercel to fetch a fresh IP for this specific thread
    try:
        # Adding a timestamp ensures we get the current node's real IP
        scraped_ip = requests.get(f'https://api.ipify.org?t={time.time()}', timeout=5).text.strip()
    except:
        scraped_ip = "Unknown"

    data = request.json
    target_url = data.get("url")
    scraper = cloudscraper.create_scraper()
    
    try:
        # 2. Perform the actual request to NoteGPT
        res = scraper.post(
            target_url, 
            json=data.get("payload"), 
            headers=data.get("headers"), 
            cookies=data.get("cookies"), 
            timeout=30
        )
        
        # 3. Build response with No-Cache instructions to force IP rotation next time
        response = Response(res.text, status=res.status_code, content_type=res.headers.get('Content-Type'))
        response.headers['X-Vercel-IP'] = scraped_ip
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        return response
    except Exception as e:
        return Response(f"Worker Error: {str(e)}", status=500)
