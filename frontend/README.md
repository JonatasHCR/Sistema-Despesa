# Firebase Studio - Full Stack App

This is a full-stack application with a Next.js frontend and a Python (FastAPI) backend.

## Frontend (Next.js)

The frontend code is located in the `/frontend` directory. To get started, `cd` into the `frontend` directory and run the development server:

```bash
cd frontend
npm install
npm run dev
```

This will start the Next.js development server, usually on port 9002.

## Backend (Python/FastAPI)

The backend code is located in the `/backend` directory. To run the backend server, you'll need to set up a Python environment and install the dependencies.

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# You'll also need to set up a .env.producao file with your DATABASE_URL
gunicorn --workers 1 --threads 8 --timeout 0 main:app
```

This will start the FastAPI backend server, usually on port 8000.

## Firebase App Hosting

This project is configured to be deployed with Firebase App Hosting. The `apphosting.yaml` file at the root of the project defines how the frontend and backend services are built and served.
