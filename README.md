# AgroManager

A full-stack agricultural management system for livestock ("ganadería") operations. Built with Django and enriched with machine learning and geospatial capabilities.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.1.2 (Python) |
| Database | SQLite3 |
| Frontend | Bootstrap 5, jQuery 3.6.0, HTML/CSS |
| Machine Learning | scikit-learn (RandomForestRegressor) |
| Geospatial | GeoPandas, Shapely, PyProj |
| Deployment | Heroku (Gunicorn + WhiteNoise) |

---

## Features

### Animal Management
- Full CRUD for cattle — species, breed, health status, birth dates, and sale status
- Bulk animal creation via CSV upload
- Filter and paginate animal listings

### Weight Tracking
- Record time-series weight measurements per animal
- Visualize weight progression on the dashboard

### Growth Prediction
- Pre-trained RandomForestRegressor model (`ml_models/modelo_crecimiento.pkl`)
- Predict future animal weight based on historical growth data

### Pasture Management
- Define grazing zones with capacity limits
- Assign animals to pasture zones
- Log weather records (temperature, rainfall) per zone

### Geospatial Mapping
- Upload field geometries in GeoJSON or WKT format
- Visualize field parcels (*campos*) on an interactive map

### Breed Management
- Manage cattle breeds (Hereford, Brahman, Angus, Charolais)
- Associate breeds with individual animals

### Dashboard & Analytics
- Total animals count
- Animals marked for sale
- Animals born this month
- Average birth weight and current weight
- Healthy animal percentage
- Mortality rate

---

## Data Models

| Model | Description |
|---|---|
| `Animal` | Core entity — identifier, species, breed, health, birth date |
| `WeightRecord` | Time-series weight measurements per animal |
| `Breed` | Cattle breed definitions |
| `PastureZone` | Grazing zones with animal capacity |
| `Campo` | Field parcels with geometry (WKT/GeoJSON) |
| `HealthRecord` | Health checkup history per animal |
| `GrowthRecord` | Growth notes and tracking |
| `WeatherRecord` | Climate data associated with pasture zones |

---

## API Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /main/` | Dashboard with statistics and charts |
| `GET /admin_animales/` | Animal list with filters and pagination |
| `POST /create_animal` | Create a new animal |
| `POST /update_animal/<id>/` | Update animal data |
| `DELETE /delete_animal/<id>/` | Delete an animal |
| `POST /add_weight_record/<id>/` | Add a weight measurement |
| `POST /carga_bulk/` | Bulk import animals from CSV |
| `GET /admin_campos/` | List field parcels |
| `POST /cargar_geojson_view/` | Upload field geometry |
| `GET /view_campo/<id>/` | View a campo on the map |
| `GET /mapeo/` | Geospatial mapping interface |
| `GET /settings_breeds/` | Breed management |
| `POST /create_breed/` | Add a breed |
| `POST /update_breed/<id>/` | Update a breed |
| `DELETE /delete_breed/<id>/` | Delete a breed |
| `POST /predict/` | Run ML growth prediction |
| `GET /input/` | Prediction input form |
| `GET /settings/` | Settings page |
| `GET /help/` | Help documentation |

---

## Project Structure

```
AgroManager/
├── agromanager_project/        # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── ganaderia/                  # Main Django application
│   ├── models.py               # Database models
│   ├── views.py                # View controllers
│   ├── admin.py                # Django admin configuration
│   ├── filters.py              # Animal query filters
│   ├── utils.py                # Geospatial utility functions
│   ├── migrations/             # Database migrations
│   ├── templates/              # HTML templates (14 files)
│   └── static/
│       ├── css/styles.css      # Main stylesheet
│       └── img/AgroLogo.jpg
├── ml_models/                  # Machine learning components
│   ├── train_model.py          # Model training script
│   ├── genera_datos.py         # Synthetic data generation
│   ├── modelo_crecimiento.pkl  # Trained RandomForest model
│   └── datos_ganado*.csv       # Training datasets
├── db.sqlite3                  # SQLite database
├── manage.py
├── Procfile                    # Heroku deployment config
└── requirements.txt
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/diegoezce/agromanager.git
cd agromanager
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/main/` in your browser.

### Retraining the ML Model (optional)

```bash
cd ml_models
python genera_datos.py   # Generate training data
python train_model.py    # Train and save the model
```

---

## Deployment

The project is configured for Heroku deployment using Gunicorn and WhiteNoise for static file serving.

```bash
# Procfile already included
heroku create
git push heroku main
```

> For production, migrate the database from SQLite to PostgreSQL.

---

## Dependencies

```
Django==5.1.2
django-filter==24.3
django_csp==3.8
gunicorn==23.0.0
whitenoise==6.8.0
pandas==2.2.3
numpy==2.1.2
scikit-learn==1.5.2
scipy==1.14.1
joblib==1.4.2
geopandas==1.0.1
shapely==2.0.6
pyproj==3.7.0
pyogrio==0.10.0
```

---

## License

This project is licensed under the MIT License.
