import os
import json
from wsgiref.simple_server import make_server
from wsgiref.util import request_uri
from urllib.parse import urlparse, parse_qs
import sqlite3
from datetime import datetime

# Database setup
DB_PATH = os.path.join('data', 'db.sqlite')

# Initialize SQLite database
def init_db():
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cache
                 (key TEXT PRIMARY KEY, value TEXT, timestamp DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS todos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  task TEXT NOT NULL,
                  completed INTEGER DEFAULT 0,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Create necessary directories
os.makedirs('static', exist_ok=True)
os.makedirs('cache', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Initialize database
init_db()

# Create cache files if they don't exist
if not os.path.exists('cache/cache.json'):
    with open('cache/cache.json', 'w') as f:
        json.dump({}, f)
if not os.path.exists('cache/data.txt'):
    with open('cache/data.txt', 'w') as f:
        f.write('')

# Cache functions
def get_cache(key):
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO cache (key, value, timestamp) VALUES (?, ?, ?)',
              (key, value, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Todo functions
def get_todos():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, task, completed FROM todos WHERE completed = 0 ORDER BY created_at DESC')
    todos = [{'id': row[0], 'task': row[1], 'completed': bool(row[2])} for row in c.fetchall()]
    conn.close()
    return todos

def add_todo(task):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO todos (task) VALUES (?)', (task,))
    todo_id = c.lastrowid
    conn.commit()
    conn.close()
    return {'id': todo_id, 'task': task, 'completed': False}

def complete_todo(todo_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE todos SET completed = 1 WHERE id = ?', (todo_id,))
    success = c.rowcount > 0
    conn.commit()
    conn.close()
    return success

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

def handle_api_todos(environ, start_response):
    method = environ['REQUEST_METHOD']
    
    if method == 'GET':
        todos = get_todos()
        start_response('200 OK', [('Content-Type', 'application/json')])
        return [json.dumps(todos).encode()]
    
    elif method == 'POST':
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            body = environ['wsgi.input'].read(content_length).decode('utf-8')
            data = json.loads(body)
            task = data.get('task', '').strip()
            
            if not task:
                start_response('400 Bad Request', [('Content-Type', 'application/json')])
                return [json.dumps({'error': 'Task cannot be empty'}).encode()]
            
            todo = add_todo(task)
            start_response('201 Created', [('Content-Type', 'application/json')])
            return [json.dumps(todo).encode()]
            
        except Exception as e:
            start_response('400 Bad Request', [('Content-Type', 'application/json')])
            return [json.dumps({'error': str(e)}).encode()]
    
    elif method == 'PUT':
        try:
            path = urlparse(environ['PATH_INFO']).path
            todo_id = int(path.split('/')[-1])
            
            if complete_todo(todo_id):
                start_response('200 OK', [('Content-Type', 'application/json')])
                return [json.dumps({'success': True}).encode()]
            else:
                start_response('404 Not Found', [('Content-Type', 'application/json')])
                return [json.dumps({'error': 'Todo not found'}).encode()]
                
        except Exception as e:
            start_response('400 Bad Request', [('Content-Type', 'application/json')])
            return [json.dumps({'error': str(e)}).encode()]
    
    start_response('405 Method Not Allowed', [('Content-Type', 'application/json')])
    return [json.dumps({'error': 'Method not allowed'}).encode()]

# Main WSGI application
def application(environ, start_response):
    uri = request_uri(environ)
    path = urlparse(uri).path
    
    # Route handling
    if path.startswith('/static/'):
        return handle_static(environ, start_response)
    elif path == '/api/todos' or path.startswith('/api/todos/'):
        return handle_api_todos(environ, start_response)
    elif path == '/':
        return handle_index(environ, start_response)
    else:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'Not Found']

if __name__ == '__main__':
    # Run development server
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever() 