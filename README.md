# NASA Hackathon – Astronautics Data Portal

This project is a full-stack web application for uploading, viewing, and downloading CSV data related to astronautics, designed for the NASA Hackathon.

## Structure
- `frontend/` – Next.js (React) app with Material UI, CSV upload, data table, download, responsive design
- `backend/` – FastAPI app with pandas, CSV upload endpoint, health-check, error handling

## Quick Start

### Backend
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run backend:
   ```bash
   python main.py
   ```

### Frontend
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Run frontend:
   ```bash
   npm run dev
   ```

### Docker
To run both frontend and backend with Docker:
```bash
docker build -t nasa-hackathon .
docker run -p 3000:3000 -p 8000:8000 nasa-hackathon
```

## Features
- Upload CSV (drag-and-drop or button)
- Data table with sorting, filtering, pagination
- Download original CSV
- Responsive design
- Error handling for invalid/empty files
- Health-check endpoint

---

**Showcase-ready for NASA Hackathon!**
