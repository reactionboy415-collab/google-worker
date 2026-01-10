from flask import Flask, request, Response
import cloudscraper

app = Flask(__name__)

# We use the root route because this file is already inside the /api folder
@app.route('/api', methods=['POST'])
def proxy_tunnel():
    data = request.json
    # Extracting the target info sent by your bot
    url = data.get("url")
    method = data.get("method", "POST")
    payload = data.get("payload")
    cookies = data.get("cookies", {})
    headers = data.get("headers", {})

    scraper = cloudscraper.create_scraper()
    
    try:
        if method == "POST":
            res = scraper.post(url, json=payload, headers=headers, cookies=cookies, timeout=25)
        else:
            res = scraper.get(url, headers=headers, cookies=cookies, timeout=25)
        
        # Return NoteGPT's response exactly as it is
        return Response(res.text, status=res.status_code, content_type=res.headers.get('Content-Type'))
    except Exception as e:
        return Response(str(e), status=500)

# Mandatory for Vercel
def handler(event, context):
    return app(event, context)
