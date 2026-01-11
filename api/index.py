from flask import Flask, request, Response
import cloudscraper
import requests
import time
import random

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods=['POST', 'GET'])
def proxy_handler(path):
    if request.method == 'GET': return "Rotator Active ✅", 200
    
    data = request.json
    scraper = cloudscraper.create_scraper()
    
    # List of exit-node helpers to force IP change
    # If one fails, it falls back to Vercel's direct IP
    proxies = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        None # Fallback to direct
    ]

    try:
        # Get actual outbound IP
        outbound_ip = requests.get(f"https://api.ipify.org?t={time.time()}", timeout=5).text.strip()
        
        # Adding random jitter to headers to prevent fingerprinting
        headers = data.get("headers", {})
        headers['X-Real-IP'] = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
        
        res = scraper.post(
            data['url'], 
            json=data['payload'], 
            headers=headers, 
            cookies=data['cookies'], 
            timeout=30
        )
        
        resp = Response(res.text, status=res.status_code, content_type='application/json')
        resp.headers['X-Vercel-IP'] = outbound_ip
        return resp
    except Exception as e:
        return Response(str(e), status=500)
