from flask import Flask, request, Response
import cloudscraper
import requests

app = Flask(__name__)

# Use a universal route to prevent 404s
@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods=['POST', 'GET'])
def catch_all(path):
    # This is for the Bot to check if the tunnel is alive
    if request.method == 'GET':
        return "Vercel Tunnel: ACTIVE ✅", 200

    # Main Tunnel Logic
    data = request.json
    target_url = data.get("url")
    method = data.get("method", "POST")
    
    # 🕵️ Get the Proxy IP (Vercel Instance IP)
    try:
        scraped_ip = requests.get('https://api.ipify.org', timeout=5).text.strip()
    except:
        scraped_ip = "Unknown"

    scraper = cloudscraper.create_scraper()
    
    try:
        if method == "POST":
            res = scraper.post(
                target_url, 
                json=data.get("payload"), 
                headers=data.get("headers"), 
                cookies=data.get("cookies"), 
                timeout=25
            )
        else:
            res = scraper.get(
                target_url, 
                headers=data.get("headers"), 
                cookies=data.get("cookies"), 
                timeout=25
            )
        
        # Send back NoteGPT's response + the Proxy IP
        response = Response(res.text, status=res.status_code, content_type=res.headers.get('Content-Type'))
        response.headers['X-Vercel-IP'] = scraped_ip
        return response
    except Exception as e:
        return Response(f"Worker Error: {str(e)}", status=500)
