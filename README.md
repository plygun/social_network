# social_network

Small Django + DRF social-network API: users, posts, likes, and a synthetic-traffic bot.

## Stack

- Python 3.10+
- Django 5.2 LTS
- Django REST Framework + SimpleJWT (access tokens)
- SQLite (development default)
- python-decouple for `.env`-based config
- Faker for the synthetic-traffic bot

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then edit DJANGO_SECRET_KEY at minimum
python manage.py migrate
python manage.py runserver    # terminal 1
python manage.py run_bot      # terminal 2 (optional)
```

## API

```
POST /v1/users/                       — sign up (anonymous)
POST /v1/token/                       — obtain JWT access + refresh
POST /v1/token/refresh/               — refresh access token
GET  /v1/users/[?page=N]              — list users (paginated)
GET  /v1/users/{id}/                  — user detail with nested posts
GET  /v1/posts/                       — list posts (auth required)
POST /v1/posts/                       — create post (auth required)
POST /v1/posts/{id}/like/             — like (idempotent — unique on user+post)
POST /v1/posts/{id}/dislike/          — remove your like
```

## Optional integrations

`HUNTER_API_KEY` enables Hunter.io email-deliverability check on signup. When unset, signup verification falls open (no third-party call, returns `True`).

`CLEARBIT_API_KEY` is wired for profile enrichment but the call path is stubbed out — Clearbit signup is gated to verified US phone numbers.

## Bot

`python manage.py run_bot` signs up `BOT_NUMBER_OF_USERS` users with fake-email accounts, has each create up to `BOT_MAX_POSTS_PER_USER` posts, then spreads up to `BOT_MAX_LIKES_PER_USER` likes per user across other users' posts. All knobs come from `.env`.
