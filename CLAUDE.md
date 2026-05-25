# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AgroManager** is a full-stack Django agricultural management system designed for livestock ("ganadería") operations. It combines animal husbandry management, real-time weight tracking, machine learning-based growth prediction, and geospatial field mapping into a single web application.

**Key Tech Stack:**
- Backend: Django 5.1.2 (Python)
- Frontend: Bootstrap 5, jQuery 3.6.0, HTML/CSS
- Database: SQLite3 (dev), PostgreSQL recommended (production)
- ML: scikit-learn RandomForestRegressor for growth prediction
- Geospatial: GeoPandas, Shapely, PyProj for field geometry handling
- Deployment: Heroku (Gunicorn + WhiteNoise)

---

## Development Setup & Commands

### Initial Setup
```bash
python -m venv venv          # Create virtual environment
source venv/bin/activate     # Activate (Linux/Mac) or venv\Scripts\activate (Windows)
pip install -r requirements.txt
python manage.py migrate     # Initialize database
python manage.py runserver   # Start dev server at http://127.0.0.1:8000/main/
```

### Common Development Commands
```bash
# Run development server
python manage.py runserver

# Create and apply migrations after model changes
python manage.py makemigrations
python manage.py migrate

# Access Django admin panel
# Create superuser first: python manage.py createsuperuser
# Then navigate to http://127.0.0.1:8000/admin/

# Retrain ML model (if modifying growth prediction)
cd ml_models
python genera_datos.py  # Generate synthetic training data
python train_model.py   # Train and save modelo_crecimiento.pkl
cd ..

# Run tests (basic test file exists at ganaderia/tests.py)
python manage.py test
```

---

## High-Level Architecture

### Project Structure
```
agromanager_project/     # Django project configuration
├── settings.py          # Database, middleware, installed apps, static files
├── urls.py              # Main URL routing
├── wsgi.py & asgi.py   # Production entry points
└── __init__.py

ganaderia/               # Main Django application (all models, views, templates)
├── models.py            # 8 core ORM models (see Models section below)
├── views.py             # View controllers and request handlers (~200 lines)
├── admin.py             # Django admin interface configuration
├── filters.py           # django-filter integration for animal queries
├── utils.py             # Geospatial utility functions (WKT/GeoJSON conversion)
├── apps.py              # App configuration
├── tests.py             # Test suite (minimal coverage)
├── migrations/          # Database schema history
├── templates/           # 13 HTML templates (base.html + feature pages)
└── static/              # CSS, images, client-side assets

ml_models/               # Machine learning components
├── modelo_crecimiento.pkl  # Pre-trained RandomForestRegressor (loaded in views.py:30)
├── train_model.py       # Training script
├── genera_datos.py      # Synthetic data generator
└── datos_ganado*.csv    # Training datasets

db.sqlite3              # Development database
requirements.txt        # Python dependencies
manage.py              # Django management interface
Procfile               # Heroku deployment config
```

### Core Data Model & Relationships

**Central Entity: Animal**
- Uniquely identified by `identifier` (string, unique)
- Has a `Breed` (foreign key) — links to breed definitions
- Tracks birth_date, birth_weight, health_status
- Can be assigned to a `PastureZone` (nullable FK)
- Marked for sale with `is_for_sale` boolean

**Time-Series & Related Data:**
- **WeightRecord** (1:N with Animal) — records weight measurements over time
- **GrowthRecord** (1:N with Animal) — growth tracking with notes
- **HealthRecord** (1:N with Animal) — health checkup history
- **SalePrediction** (1:N with Animal) — predicted sale date/weight/market price

**Pasture & Geospatial:**
- **PastureZone** — named grazing areas with area_size, grazing_capacity; M:N with Animal (via current_animals)
- **WeatherRecord** (1:N with PastureZone) — temperature, rainfall logs
- **Campo** — field parcels stored with WKT geometry; supports GeoJSON import

---

## Key Features & Common Workflows

### 1. Animal Management (views.py: `admin_animales`, `create_animal`, `update_animal`, `delete_animal`)
- List animals with filtering (AnimalFilter in filters.py) and pagination (Paginator)
- Filter by identifier, species, breed, health_status, birth_date range
- Create/update/delete via forms
- **Bulk Import:** CSV upload in `carga_bulk` endpoint — parses CSV and creates multiple Animal records

### 2. Weight Tracking & Growth Visualization
- Add weight records via `add_weight_record` endpoint
- Dashboard displays latest weight per animal
- Uses `Animal.latest_weight()` and `Animal.latest_weight_recorded()` helper methods

### 3. Growth Prediction (ML)
- **Workflow:** User provides birth_date, breed, pasture_zone, health_status, current_date, current_weight → model predicts weight
- **Model:** Pre-trained scikit-learn pipeline in `ml_models/modelo_crecimiento.pkl` (loaded at app startup in views.py:30)
- **Endpoints:** `/input/` (form) and `/predict/` (POST with form data)
- **Data Preparation:** Input data converted to pandas DataFrame, passed through pipeline
- **Important:** Pipeline expects specific features matching training data; if adding new animal attributes, model retraining may be needed

### 4. Geospatial Mapping (utils.py, views.py)
- **Geometry Storage:** Stored as WKT strings in Campo model
- **Import Formats:** GeoJSON (file upload) or WKT (direct)
- **Conversion:** Shapely handles GeoJSON ↔ WKT; GeoPandas enables spatial operations
- **Visualization:** Interactive map in mapeo template (likely using Leaflet or Folium)
- **Endpoints:** `/mapeo/`, `/cargar_geojson_view/`, `/view_campo/<id>/`

### 5. Dashboard & Analytics (main_view, main.html)
- Displays:
  - Total animal count
  - Animals marked for sale (is_for_sale=True)
  - Animals born this month
  - Average birth weight & current weight
  - Healthy animal percentage
  - Mortality rate

---

## Important Implementation Details

### Django Admin (admin.py)
Register models here to enable admin interface management. Check `admin.py` to see which models are exposed.

### URL Routing (agromanager_project/urls.py)
Main URL patterns map to ganaderia views. Routes like `/admin_animales/`, `/main/`, `/predict/` are defined here.

### Static Files & Deployment (settings.py)
- WhiteNoise middleware handles static file serving in production
- CSS in `ganaderia/static/css/styles.css`
- Images in `ganaderia/static/img/`
- For production, collect static files: `python manage.py collectstatic`

### CSRF & Security (settings.py)
- CSRF protection enabled by default
- django-csp (Content Security Policy) installed but check settings for active configuration

---

## Common Development Patterns

### Adding a New Feature
1. **Model Changes:** Modify `ganaderia/models.py`, then run `makemigrations` and `migrate`
2. **Views:** Add new view function in `ganaderia/views.py`, import any new models
3. **URL Routing:** Add route in `agromanager_project/urls.py`
4. **Templates:** Create new HTML in `ganaderia/templates/`, extend `base.html` for consistency
5. **Admin Interface:** Register new model in `ganaderia/admin.py` if needed

### Working with the ML Model
- Model is **pre-trained** and loaded at startup (views.py line 30)
- To retrain: `cd ml_models && python genera_datos.py && python train_model.py`
- Features expected by model are defined in `train_model.py` — if you add new Animal attributes, retraining may be needed
- Predictions happen in `predict_growth` view using joblib-loaded pipeline

### Filtering Animals
- `AnimalFilter` (filters.py) integrates with django-filter
- Used in `admin_animales` view with GET parameters
- Add new filter fields by modifying AnimalFilter class

### Geospatial Operations
- All geometry stored as WKT in Campo.geometria field
- Shapely's `shape()` converts GeoJSON → geometry; `.wkt` converts back
- Use `cargar_datos_geoespaciales()` utility in utils.py for imports

---

## Production & Deployment Notes

### Database Migration
- Currently SQLite3 (suitable for development only)
- For production: configure PostgreSQL in `settings.py` (DATABASES section)
- Update requirements.txt to include psycopg2 (PostgreSQL adapter)

### Environment Variables
- `SECRET_KEY` is hardcoded in settings.py — move to environment variable for production
- `DEBUG` must be False in production
- `ALLOWED_HOSTS` must include your domain

### Heroku Deployment
- Procfile already configured: `web: gunicorn agromanager_project.wsgi`
- Steps: `heroku create`, `git push heroku main`
- Ensure PostgreSQL add-on is provisioned on Heroku

---

## Testing

Basic test skeleton exists in `ganaderia/tests.py`. To add tests:
```bash
python manage.py test ganaderia.tests
```

Key areas to test:
- Model methods like `Animal.latest_weight()`
- View responses and redirects
- Filter functionality
- ML prediction accuracy (mock predictions)
- Geospatial geometry conversions

---

## Useful Resources Within the Codebase

- **README.md** — Feature overview, API endpoints, getting started
- **requirements.txt** — All dependencies with pinned versions
- **Procfile** — Production entry point
- **Django Docs:** https://docs.djangoproject.com/en/5.1/

---

## Notes for Future Development

1. **Model Prediction Complexity:** The ML growth prediction assumes specific input features. If the Animal model is extended (e.g., new health attributes), the training pipeline in `ml_models/train_model.py` must be updated and the model retrained.

2. **Geospatial Performance:** If working with large GIS datasets, consider spatial indexes on Campo.geometria in PostgreSQL.

3. **Frontend Interactivity:** Templates use jQuery 3.6.0. Consider upgrading to vanilla JS or a modern framework if adding significant frontend features.

4. **Data Validation:** Input validation happens both client-side (HTML5) and server-side (Django forms/models). Ensure consistency.

5. **Error Handling:** Current error handling is basic. Consider adding logging and more detailed error messages for production.

