# 🚀 Penvis Realtime Chat

![Django](https://img.shields.io/badge/Django-Backend-green)
![WebSockets](https://img.shields.io/badge/WebSockets-Realtime-blue)
![Redis](https://img.shields.io/badge/Redis-Channel%20Layer-red)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

A modern **realtime chat platform** built with **Django, Django
Channels, WebSockets, and Redis** designed for deployment on a **Linux
VPS with Nginx and HTTPS**.

------------------------------------------------------------------------

# ✨ Features

-   ⚡ Realtime messaging with WebSockets
-   👥 Multi‑user chat
-   🔐 Authentication system
-   📁 File & media upload
-   🧠 Redis powered message broker
-   🌐 Production ready
-   🔒 HTTPS support
-   🚀 VPS deployment ready
-   🧩 Modular Django apps

------------------------------------------------------------------------

# 🧱 Tech Stack

  Layer            Technology
  ---------------- -----------------
  Backend          Django
  Realtime         Django Channels
  Protocol         WebSockets
  Message Broker   Redis
  ASGI Server      Daphne
  Reverse Proxy    Nginx
  Deployment       Linux VPS

------------------------------------------------------------------------

# 📂 Project Structure

    project-root
    │
    ├── vpschat/
    │   ├── settings.py
    │   ├── asgi.py
    │   └── urls.py
    │
    ├── apps/
    ├── templates/
    ├── static/
    ├── manage.py
    ├── requirements.txt
    ├── .env.example
    └── README.md

------------------------------------------------------------------------

# 🛠 Installation (Local)

## 1. Clone

    git clone https://github.com/YOUR_USERNAME/penvis-realtime-chat.git
    cd penvis-realtime-chat

## 2. Virtual Environment

    python -m venv venv
    source venv/bin/activate

## 3. Install Dependencies

    pip install -r requirements.txt

## 4. Setup Environment

    cp .env.example .env

Example:

    DEBUG=True
    SECRET_KEY=change-me
    ALLOWED_HOSTS=127.0.0.1,localhost
    DATABASE_URL=sqlite:///db.sqlite3
    REDIS_URL=redis://127.0.0.1:6379

## 5. Migrate

    python manage.py migrate

## 6. Run

    python manage.py runserver

------------------------------------------------------------------------

# ⚡ Redis Setup

Ubuntu:

    sudo apt install redis-server
    sudo systemctl start redis

Mac:

    brew install redis
    brew services start redis

------------------------------------------------------------------------

# 🚀 Deploy on VPS

Install packages

    sudo apt update
    sudo apt install python3-pip python3-venv nginx redis git

Clone

    git clone https://github.com/YOUR_USERNAME/penvis-realtime-chat.git

Setup

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Run migrations

    python manage.py migrate
    python manage.py collectstatic

Run Daphne

    daphne -b 127.0.0.1 -p 8001 vpschat.asgi:application

------------------------------------------------------------------------

# 🌍 Nginx Example

    server {
        server_name chat.penvis.ir;

        location / {
            proxy_pass http://127.0.0.1:8001;
            proxy_http_version 1.1;

            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";

            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }

------------------------------------------------------------------------

# 🔐 Enable HTTPS

    sudo certbot --nginx -d chat.penvis.ir

------------------------------------------------------------------------

# 🔑 Environment Variables

  Variable        Description
  --------------- ------------------
  SECRET_KEY      Django secret
  DEBUG           Debug mode
  ALLOWED_HOSTS   Allowed domains
  DATABASE_URL    Database
  REDIS_URL       Redis
  MEDIA_ROOT      Upload directory

------------------------------------------------------------------------

# 🗺 Roadmap

-   Reactions
-   Message edit
-   Notifications
-   Mobile UI
-   Chat rooms
-   Voice messages

------------------------------------------------------------------------

# 👨‍💻 Author

**Penvis Project**

------------------------------------------------------------------------

# ⭐ Support

If you like this project give it a **star ⭐ on GitHub**.
