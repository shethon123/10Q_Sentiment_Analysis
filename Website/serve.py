#!/usr/bin/env python3
"""Simple dev server for SentinelIQ frontend — run while api.py is also running."""
import http.server
import webbrowser
import os

PORT = 3001

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress per-request noise

print(f"SentinelIQ frontend → http://localhost:{PORT}/SentinelIQ.html")
webbrowser.open(f"http://localhost:{PORT}/SentinelIQ.html")
http.server.HTTPServer(("", PORT), Handler).serve_forever()
