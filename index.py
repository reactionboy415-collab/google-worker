from flask import Flask, request, Response
import cloudscraper
import requests

app = Flask(__name__)

@app.route('/api', methods=['POST', 'GET'])
def proxy_tunnel():
    # Only process POST for the tunnel
    if request.method == 'POST':
        data = request.json
        url = data.get("url")
        method = data.get("method", "POST")
        payload = data.get("payload")
        cookies = data.get("cookies", {})
        headers = data.get("headers", {})

        scraper = cloudscraper.create_scraper()
        
        # 🛡️ Get the current Vercel Instance IP (The "Scraped Proxy")
        try:
            vercel_ip = requests.get('https://ifconfig.me', timeout=5).text.strip()
        except:
            vercel_ip = "Unknown"

        try:
            if method == "POST":
                res = scraper.post(url, json=payload, headers=headers, cookies=cookies, timeout=25)
            else:
                res = scraper.get(url, headers=headers, cookies=cookies, timeout=25)
            
            # Send back NoteGPT's response + the Vercel IP in a header
            response = Response(res.text, status=res.status_code, content_type=res.headers.get('Content-Type'))
            response.headers['X-Vercel-IP'] = vercel_ip
            return response
        except Exception as e:
            return Response(str(e), status=500)
    
    return "Vercel Tunnel Active", 200

# Mandatory for Vercel
def handler(event, context):
    return app(event, context)
