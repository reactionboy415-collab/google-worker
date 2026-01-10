from flask import Flask, request, Response
import cloudscraper
import requests
import time

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods=['POST', 'GET'])
def proxy(path):
    if request.method == 'GET': return "Tunnel Active", 200
    
    # Force fresh IP fetch
    try:
        scraped_ip = requests.get(f"https://api.ipify.org?t={time.time()}", timeout=5).text.strip()
    except: scraped_ip = "Unknown"

    data = request.json
    scraper = cloudscraper.create_scraper()
    
    try:
        res = scraper.post(data['url'], json=data['payload'], headers=data['headers'], cookies=data['cookies'], timeout=30)
        resp = Response(res.text, status=res.status_code, content_type='application/json')
        resp.headers['X-Vercel-IP'] = scraped_ip
        return resp
    except Exception as e:
        return Response(str(e), status=500)
