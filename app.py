import os
import json
from wsgiref.simple_server import make_server
from wsgiref.util import request_uri
from urllib.parse import urlparse
import sqlite3
from datetime import datetime

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cache
                 (key TEXT PRIMARY KEY, value TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

# Cache functions
def get_cache(key):
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    c.execute('SELECT value, timestamp FROM cache WHERE key = ?', (key,))
    result = c.fetchone()
    conn.close()
    
    if result:
        value, timestamp = result
        # Check if cache is expired (24 hours)
        if (datetime.now() - datetime.fromisoformat(timestamp)).total_seconds() < 86400:
            return value
    return None

def set_cache(key, value):
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO cache (key, value, timestamp) VALUES (?, ?, ?)',
              (key, value, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Route handlers
def handle_static(environ, start_response):
    uri = request_uri(environ)
    path = urlparse(uri).path
    static_path = os.path.join('static', path.lstrip('/'))
    
    if os.path.exists(static_path):
        with open(static_path, 'rb') as f:
            content = f.read()
        content_type = 'text/plain'
        if path.endswith('.html'):
            content_type = 'text/html'
        elif path.endswith('.css'):
            content_type = 'text/css'
        elif path.endswith('.js'):
            content_type = 'application/javascript'
            
        start_response('200 OK', [('Content-Type', content_type)])
        return [content]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'Not Found']

def handle_index(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    with open('static/index.html', 'rb') as f:
        return [f.read()]

# Main WSGI application
def application(environ, start_response):
    uri = request_uri(environ)
    path = urlparse(uri).path
    
    # Route handling
    if path.startswith('/static/'):
        return handle_static(environ, start_response)
    elif path == '/':
        return handle_index(environ, start_response)
    else:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'Not Found']

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static', exist_ok=True)
    os.makedirs('cache', exist_ok=True)
    
    # Initialize database
    init_db()
    
    # Create cache files if they don't exist
    if not os.path.exists('cache/cache.json'):
        with open('cache/cache.json', 'w') as f:
            json.dump({}, f)
    if not os.path.exists('cache/data.txt'):
        with open('cache/data.txt', 'w') as f:
            f.write('')
    
    # Run development server
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever() 