🔗 Live demo: https://bit-notes-app.onrender.com

# BIT Notes

A web app for BIT students to upload and share study notes.

## Built With
- Python + Flask
- SQLite + SQLAlchemy
- HTML/CSS/JavaScript

## Features
- Register and login
- Upload notes (PDF/images) by subject
- Browse and filter by subject
- Download notes

## How to Run Locally
1. Clone the repo
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python app.py`
6. Open: http://127.0.0.1:5000


git init
git add .
git commit -m "initial commit - BIT notes app with upload, browse, delete"
git branch -M main
git remote add origin https://github.com/samish-bit/bit-notes-app.git
git push -u origin main
