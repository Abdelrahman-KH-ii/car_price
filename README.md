# CarValue — Car Price Predictor

Django web app backed by an XGBoost model that predicts used-car prices.
Supports **SQLite** (local dev) and **PostgreSQL** (production).

---

## Project Structure

```
carproject/
├── carprice/          # Django project (settings, urls, wsgi)
├── accounts/          # Register / Login / Logout
├── predictor/         # Home, Predict form, Result + XGBoost model
│   └── best_xgb_model.pkl
├── templates/
├── static/
├── nginx/
│   ├── nginx.conf          # HTTPS (production)
│   └── nginx.http.conf     # HTTP-only (no SSL)
├── Dockerfile
├── docker-compose.yml           # Local dev
├── docker-compose.prod.yml      # Production
├── requirements.txt
├── .env                         # Local dev vars (not committed)
├── .env.production              # Production vars (not committed)
└── .env.example                 # Template — copy and fill
```

---

## 1 — Run Locally (no Docker)

```bash
# 1. Create & activate virtualenv
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install deps
pip install -r requirements.txt

# 3. Copy env file
cp .env.example .env
# Edit .env — set DEBUG=True, DB_ENGINE=sqlite  (defaults already set)

# 4. Migrate & run
python manage.py migrate
python manage.py runserver
```

Open → http://127.0.0.1:8000

---

## 2 — Run with Docker (local dev, SQLite)

```bash
docker compose up --build
```

Open → http://localhost:8000

---

## 3 — Production Deploy (Docker + Postgres + Nginx)

### Step 1 — Fill production env
```bash
cp .env.example .env.production
nano .env.production
# Set: SECRET_KEY, ALLOWED_HOSTS, DB_NAME, DB_USER, DB_PASSWORD
# DB_ENGINE=postgres
# DEBUG=False
```

### Step 2 — SSL certs
Place your SSL certificate files in `nginx/certs/`:
```
nginx/certs/fullchain.pem
nginx/certs/privkey.pem
```
> For Let's Encrypt use Certbot. For HTTP-only (no SSL), replace
> `nginx/nginx.conf` with the contents of `nginx/nginx.http.conf`.

### Step 3 — Update nginx.conf domain
Edit `nginx/nginx.conf` → replace `yourdomain.com` with your actual domain.

### Step 4 — Deploy
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

The stack starts:
- `db`    — PostgreSQL 16
- `web`   — Gunicorn (3 workers)
- `nginx` — reverse proxy on ports 80 & 443

### Step 5 — Create superuser (optional)
```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### Useful commands
```bash
# View logs
docker compose -f docker-compose.prod.yml logs -f web

# Run migrations manually
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Stop everything
docker compose -f docker-compose.prod.yml down

# Stop and delete volumes (wipes DB!)
docker compose -f docker-compose.prod.yml down -v
```

---

## 4 — Deploy on PythonAnywhere (free tier)

PythonAnywhere doesn't support Docker, so deploy directly:

```bash
# 1. Open a Bash console on PythonAnywhere
git clone https://github.com/youruser/carvalue.git
cd carvalue

# 2. Create virtualenv
mkvirtualenv carvalue --python=python3.11
pip install -r requirements.txt

# 3. Set env vars — PythonAnywhere → Files → create a .env file
#    OR export manually in the WSGI file (see step 5)

# 4. Migrate & collect static
python manage.py migrate
python manage.py collectstatic --noinput

# 5. WSGI file — PythonAnywhere → Web → WSGI configuration file
```

Paste this in the WSGI file:
```python
import os, sys
from decouple import config

path = '/home/YOURUSERNAME/carvalue'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'carprice.settings'
os.environ['SECRET_KEY']    = 'your-secret-key'
os.environ['DEBUG']         = 'False'
os.environ['ALLOWED_HOSTS'] = 'YOURUSERNAME.pythonanywhere.com'
os.environ['DB_ENGINE']     = 'sqlite'   # free tier: sqlite is fine

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

```
6. Static files — PythonAnywhere → Web → Static files:
   URL: /static/
   Dir: /home/YOURUSERNAME/carvalue/staticfiles

7. Hit Reload → your app is live at YOURUSERNAME.pythonanywhere.com
```

---

## 5 — Run Tests

```bash
python manage.py test --verbosity=2
```

Expected: **33 tests, 0 errors, 0 failures**

Coverage areas:
- Register: success, duplicate username/email, missing fields, redirect-if-logged-in
- Login: success, wrong password, non-existent user, redirect-if-logged-in
- Logout: redirect to home, session cleared
- Home: page loads, arrow link present
- Predict: login required, page loads, username shown, brand/model data present
- API `/api/models/`: valid brand, unknown brand, no brand param
- Result: POST with valid data, premium car, missing field graceful, details shown
- Navigation: login/logout in navbar based on auth state

---

## 6 — Future (ready to add)

The codebase is structured to easily add:
- Phone number verification (e.g. Twilio)
- Email verification (Django allauth)
- Google OAuth (Django allauth)

These will live in `accounts/` with minimal changes to the existing views.
