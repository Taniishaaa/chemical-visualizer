# Chemical Equipment Parameter Visualizer

Hybrid Web + Desktop Application — Internship Screening Task

## Overview

This project is a hybrid Web + Desktop application for analyzing chemical equipment datasets.
Users can upload a CSV file and instantly view:

## Summary analytics

Visualizations

Upload history

Downloadable PDF reports

Both the web (React) and desktop (PyQt5) apps communicate with the same Django REST API.

## Project Structure

chemical-equipment-visualizer/
│
├── backend/               - Django REST API
│   ├── core/              - Project settings
│   ├── equipment/         - API logic
│   ├── db.sqlite3
│   ├── manage.py
│   └── requirements.txt
│
├── web-frontend/          - React + Vite frontend
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
└── desktop-app/           - PyQt5 desktop viewer
    └── main.py

## Features

### CSV Upload

Supports CSV files containing:
Equipment Name | Type | Flowrate | Pressure | Temperature

### Data Analytics

Total equipment count

Average pressure

Average flowrate

Average temperature

Equipment type distribution

### Visualizations

Web: Chart.js bar chart

Desktop: Matplotlib bar chart

### Upload History

Backend stores and returns the last 5 uploaded datasets.

### Basic Authentication

Entire backend protected using BasicAuth.
Frontend apps send credentials automatically.

### PDF Report

Backend generates a downloadable PDF summary for each dataset.

### Desktop Application

Upload CSV

View summary

View chart

View upload history

Download PDF

## Setup Instructions

1. Clone the Repository

git clone <your-repository-url>
cd chemical-equipment-visualizer

2. Backend Setup (Django API)

Create Virtual Environment:
python -m venv venv
venv\Scripts\activate      - Windows
- or: source venv/bin/activate

Install Dependencies:
pip install -r backend/requirements.txt

Apply Migrations:
cd backend
python manage.py migrate

Create Superuser:
python manage.py createsuperuser

Run Backend:
python manage.py runserver


Backend runs at: http://127.0.0.1:8000/

3. Web Frontend Setup (React + Vite)

Open a separate terminal:

cd web-frontend
npm install
npm run dev


Runs at: http://localhost:5173/

4. Desktop App Setup

Run:

cd desktop-app
python main.py

## Sample CSV

A sample dataset is included for demonstration.

## Authentication

Backend uses Basic Authentication.

Frontend credentials configured here:

web-frontend/src/App.jsx

desktop-app/main.py

Example:

username: tanisha
password: tanisha123

Modify these if needed.

## Running All Components Together

Terminal 1 → Start backend

python manage.py runserver


Terminal 2 → Start React

npm run dev


Terminal 3 → Start Desktop App

python main.py

## API Endpoints

Endpoint: /api/upload-csv/	

Method: POST	

Description: Upload CSV + compute summary

Endpoint: /api/history/	

Method: GET	

Description: Fetch last 5 uploads

Endpoint: /api/report/<id>/	

Method: GET	

Description: Download PDF report


