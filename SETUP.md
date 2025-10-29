# Setup Guide

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ and npm installed
- Git (optional)

## Installation Steps

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# (Optional) Create .env file
copy .env.example .env
# Edit .env and set your SECRET_KEY
```

### 2. Install All Dependencies

From the root directory:
```bash
npm install
npm run install:all
```

Or manually:
```bash
# Frontend dependencies
cd frontend
npm install

# Backend dependencies
cd ../backend
pip install -r requirements.txt
```

## Running the Application

### Quick Start (Recommended)

From the root directory:
```bash
npm run dev
```

This will start both the backend and frontend servers automatically.

### Alternative Options

**Option 1: Windows Batch File**
Double-click `start-dev.bat` in the root directory.

**Option 2: Manual Start**

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Access the Application

- **Frontend UI:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## First Time Usage

1. Open http://localhost:5173 in your browser
2. Register a new account using the Register form
3. Login with your credentials
4. Once logged in, you can upload videos

## Troubleshooting

### Backend won't start
- Make sure Python is installed: `python --version`
- Check if port 8000 is available
- Verify all dependencies are installed: `pip list`

### Frontend won't start
- Make sure Node.js is installed: `node --version`
- Check if port 5173 is available
- Try deleting `node_modules` and running `npm install` again

### CORS errors
- Ensure backend is running on port 8000
- Check that frontend is accessing http://localhost:8000

### Upload fails
- Check that you're logged in (token is displayed)
- Verify the backend is running
- Check browser console for errors

## Production Deployment

For production deployment:

1. **Backend:**
   - Set a strong SECRET_KEY in environment variables
   - Replace in-memory storage with a database (PostgreSQL, MongoDB)
   - Set up proper file storage (AWS S3, etc.)
   - Use a production WSGI server (gunicorn)
   - Enable HTTPS

2. **Frontend:**
   - Build the production bundle: `npm run build`
   - Update API_URL to your production backend URL
   - Deploy to Netlify, Vercel, or your hosting service
   - Enable HTTPS

3. **Security:**
   - Use environment variables for all secrets
   - Enable rate limiting
   - Add input validation
   - Implement proper error handling
   - Set up monitoring and logging
