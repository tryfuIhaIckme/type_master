# Deployment Guide for TypeMaster


## 1. Prerequisites
- Python 3.12+
- Nginx
- Virtualenv

## 2. Setup on Server
```bash

git clone <your-repo-url>
cd type_master

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

## 3. Environment Variables
Create a `.env` file or set environment variables in your system:
- `SECRET_KEY`: A long random string for security.
- `FLASK_DEBUG`: Set to `False` in production.
- `DATABASE_URL`: Defaults to local SQLite if not provided.

## 4. Running with Gunicorn
To start the server in production mode:
```bash
gunicorn --bind 0.0.0.0:8000 wsgi:app
```

## 5. Nginx Configuration
Recommended Nginx proxy block:
```nginx
location / {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```
