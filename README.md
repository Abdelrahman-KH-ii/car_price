#  CarValue — Used Car Price Predictor

A Django-based web application that predicts used car prices using an XGBoost machine learning model.

---

##  Deployment Status

The project is currently not deployed due to the high memory requirements of the machine learning model and dependencies, which exceed the limitations of free-tier hosting services.

However, the full functionality of the application can be demonstrated through the following video:

https://drive.google.com/file/d/1C5MhUftPnYQtS3qU9g-Jr8woqokaJr89/view?usp=sharing

If you would like to try the application yourself, you can run it locally using Docker as shown below.

---

## Quick Start

```bash id="k2r8av"
git clone https://github.com/Abdelrahman-KH-ii/car_price.git
cd car_price
docker compose up --build
```

Open in your browser:
http://localhost:8000

---

##  Tech Stack

Django · XGBoost · PostgreSQL · Docker · Nginx · Gunicorn · WhiteNoise

---

##  Features

* User registration and authentication
* 27 car brands and 150+ models with dynamic auto-fill
* Price prediction in INR (Lakh) with USD equivalent
* REST API endpoint for model selection
* 37 automated tests covering core functionality
