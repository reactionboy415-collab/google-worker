from flask import Flask, request, Response
import cloudscraper
import requests

app = Flask(__name__)

# This catches everything sent to /api
@app.route('/api', methods=['POST', 'GET'], defaults={'path': ''})
@app.route('/api/<path:path>', methods=['POST', 'GET'])
def proxy_tunnel(path):
    if request.method == 'POST':
        data = request.json
        url = data.get("url")
        # Get the IP of the current Vercel container
        try:
            vercel_ip = requests.get('https://api.ipify.org', timeout=5).text.strip()
        except:
            vercel_ip = "Unknown"

        scraper = cloudscraper.create_scraper()
        
        try:
            res = scraper.post(url, json=data.get("payload"), headers=data.get("headers"), cookies=data.get("cookies"), timeout=25)
            response = Response(res.text, status=res.status_code, content_type=res.headers.get('Content-Type'))
            response.headers['X-Vercel-IP'] = vercel_ip
            return response
        except Exception as e:
            return Response(str(e), status=500)

    return f"Vercel Tunnel Status: ACTIVE. Path: {path}", 200

# Required for Vercel
def handler(event, context):
    return app(event, context)
