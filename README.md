# Python WSGI Template Project

A minimal, flexible web application template using raw WSGI, Gunicorn, and Nginx.

## Features

- Raw WSGI implementation (no frameworks)
- Gunicorn WSGI server
- Nginx reverse proxy and static file serving
- SQLite database
- JSON/TXT caching system
- Docker and Docker Compose setup
- Modern, responsive frontend

## Tech Stack

- Python 3.11
- Gunicorn (WSGI)
- Nginx (proxy/static)
- Docker
- Docker Compose
- SQLite
- requests (for API calls)

## Project Structure

```
.
├── app.py              # Main WSGI application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Python application container
├── docker-compose.yml # Container orchestration
├── nginx.conf         # Nginx configuration
├── static/            # Static files
│   ├── index.html
│   ├── style.css
│   └── script.js
├── cache/            # Cache directory
│   ├── cache.json
│   └── data.txt
└── db.sqlite         # SQLite database
```

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Build and start the containers:

   ```bash
   docker-compose up --build
   ```

3. Access the application:
   - Main application: http://localhost
   - Static files: http://localhost/static/\*

## Development

- The application runs on port 8000 internally
- Nginx proxies requests from port 80 to the application
- Static files are served directly by Nginx
- Cache files are stored in the `cache/` directory
- Database is stored in `db.sqlite`

## API Endpoints

- `GET /`: Main page
- `GET /static/*`: Static file serving

## Customization

1. Modify `app.py` to add new routes and functionality
2. Update `static/` files for frontend changes
3. Adjust `nginx.conf` for custom Nginx settings
4. Modify `docker-compose.yml` for container configuration

## License

MIT License
