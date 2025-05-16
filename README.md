# TradersPortal Backend

A Django 5.1 + DRF project implementing:

- **JWT Authentication** (register, login via username/email, logout, token refresh)
- **Company** & **Watchlist** models (indexed for performance)
- **Search & filter** companies with `django-filters` + DRF `SearchFilter`
- **Add/remove** companies on user’s watchlist
- **Error handling** & **logging** (to console & `app_errors.log`)
- **Rate limiting** with DRF throttling
- **Background import** of company data via Celery + django‑celery‑beat
- **API docs** via Swagger (drf‑yasg)
- **Deployment** instructions (local, ngrok, Heroku)

---

## 🔧 Requirements

- Python 3.10+
- Redis (for Celery broker)
- (Optional) ngrok for public tunneling

---

## ⚙️ Local Setup

1. **Clone & install**:

   ```bash
   git clone <repo-url>
   cd TradersPortal
   python3 -m venv env && source env/bin/activate
   pip install -r requirements.txt
   ```

2. **Create environment variables** (e.g. in a `.env` file or export):

   ```bash
   export SECRET_KEY="your-secret-key"
   export DEBUG=True
   ```

3. **Migrate & create superuser**:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Start Redis** (for Celery):
   ```bash
   sudo service redis-server start
   ```

---

## 🚀 Running Locally

In **three** terminals:

```bash
# Terminal 1: Django server
python manage.py runserver 0.0.0.0:8000

# Terminal 2: Celery worker
celery -A TradersPortal worker --loglevel=info

# Terminal 3: Celery beat scheduler
celery -A TradersPortal beat --loglevel=info
```

---

## 🗂️ Models

### 1. Company

```python
company_name: CharField
symbol      : CharField(unique, indexed)
scripcode   : CharField(unique, indexed)
```

### 2. Watchlist

```python
user         : ForeignKey(User)
company      : ForeignKey(Company)
added_on     : DateTimeField(auto_now_add)
unique_together: (user, company)
```

---

## 📱 Authentication (JWT)

- **Register**:  
  `POST /auth/register/`
- **Login**:  
  `POST /auth/login/`
  ```json
  { "username": "...", "password": "..." }
  ```
  → returns
  ```json
  { "refresh": "...", "access": "..." }
  ```
- **Refresh**:  
  `POST /auth/token/refresh/`
- **Logout**:  
  `POST /auth/logout/`

Use header on protected endpoints:

```
Authorization: Bearer <access_token>
```

---

## 🔍 Companies API

`GET /companies/`

Query parameters:

- `search=` (searches `company_name`, `symbol`, `scripcode`)
- `symbol=` (startswith)
- `company_name=` (icontains)

Pagination: `limit` & `offset`  
Throttling: **100 req/hr** (authenticated), **50 req/hr** (anonymous)

---

## ⭐ Watchlist API

- `GET /watchlist/`
- `POST /watchlist/add/`
  ```json
  { "company_id": 42 }
  ```
- `DELETE /watchlist/remove/{company_id}/`

_All watchlist endpoints require JWT authentication._

---

## 🛠 Error Handling & Logging

- Uses DRF exceptions: `ValidationError`, `NotFound`, `APIException`
- Returns appropriate HTTP status codes (`200`, `201`, `400`, `401`, `404`, `500`)
- Logs errors to console and `app_errors.log` (configured in `settings.py`)

---

## ⚡ Rate Limiting

Configured in `settings.py`:

```python
REST_FRAMEWORK = {
  'DEFAULT_THROTTLE_CLASSES': [
    'rest_framework.throttling.UserRateThrottle',
    'rest_framework.throttling.AnonRateThrottle',
  ],
  'DEFAULT_THROTTLE_RATES': {
    'user': '100/hour',
    'anon': '50/hour',
  },
  ...
}
```

---

## 🕒 Background Tasks (Celery)

- **Task**: `companies.tasks.import_companies_task`
- **Function**: Fetches CSV from Google Drive & upserts Company records
- **Scheduler**: django‑celery‑beat (configure via Admin → Periodic Tasks)

---

## 📚 API Documentation (Swagger)

1. **Install** drf‑yasg and add to `INSTALLED_APPS`.
2. **Configure** in `urls.py`:

   ```python
   from drf_yasg.views import get_schema_view
   from drf_yasg import openapi
   from rest_framework import permissions

   schema_view = get_schema_view(
     openapi.Info(
       title="TradersPortal API",
       default_version='v1',
       description="Auth, Companies, Watchlist",
     ),
     public=True,
     permission_classes=(permissions.AllowAny,),
   )

   urlpatterns += [
     path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
     path('redoc/',  schema_view.with_ui('redoc',  cache_timeout=0)),
   ]
   ```

3. **CORS & HTTPS**: Use `corsheaders` and expose via ngrok.
4. **Authorize**: Click **Authorize** in Swagger, enter `Bearer <access_token>`.

Visit locally:

```
http://127.0.0.1:8000/swagger/
```

Share publicly via ngrok:

```
https://6fd5-2401-4900-1f2c-49a1-a4ce-b658-5276-6148.ngrok-free.app//swagger/
```

Invite **abdul.jaseem@tradebrains.in** as needed.

---

## ☁️ Deployment

### Local + Nginx

1. Install Nginx & configure proxy to Gunicorn on `localhost:8000`.
2. Obtain HTTPS certs (e.g., Let’s Encrypt).

### Heroku

```bash
heroku create your-app
heroku addons:create heroku-redis
git push heroku main
heroku run python manage.py migrate
heroku config:set SECRET_KEY="your-secret"
```

### ngrok (Temporary)

```bash
ngrok http 8000
```

Use the HTTPS forwarding URL for demos, webhooks, and shared Swagger UI.
