# NPM Commands Guide

## 🚀 Quick Start (One Command!)

```bash
npm run dev
```

This starts both backend and frontend servers in one terminal!

---

## 📦 First Time Setup

### Install Everything

```bash
npm run install:all
```

This installs:
- Root dependencies (concurrently)
- Frontend dependencies (React, Vite, etc.)
- Backend dependencies (FastAPI, etc.)

### Or Install Separately

**Backend only:**
```bash
npm run install:backend
```

**Frontend only:**
```bash
npm run install:frontend
```

---

## 🎮 Available Commands

### Development

```bash
npm run dev
# or
npm start
```
Starts both servers:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

### Individual Servers

**Backend only:**
```bash
npm run dev:backend
```

**Frontend only:**
```bash
npm run dev:frontend
```

---

## 📝 Step-by-Step First Time Setup

### 1. Install Dependencies

```bash
npm run install:all
```

Wait for all packages to install...

### 2. Configure Backend

Create `backend/.env` file:

```bash
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
ENVIRONMENT=development
```

Get Gemini API key: https://aistudio.google.com/app/apikey

### 3. Start Development

```bash
npm run dev
```

### 4. Open Browser

Go to: http://localhost:5173

### 5. Dev Login

Click the purple "Dev Login" button

### 6. Seed Data

Click the purple "Seed Sample Data" button

### 7. Explore!

- Dashboard - See analytics
- Clips Library - Browse clips
- Generate Clips - Create new clips

---

## 🛑 Stopping Servers

Press `Ctrl+C` in the terminal

This will stop both servers automatically.

---

## ❓ Troubleshooting

### "concurrently: command not found"

Install root dependencies:
```bash
npm install
```

### "Python not found"

Install Python 3.8+ from: https://www.python.org/downloads/

### "npm not found"

Install Node.js 16+ from: https://nodejs.org/

### Port Already in Use

Kill processes using ports 8000 or 5173:

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F

netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

**Or just restart your computer** 😅

### Backend Won't Start

Check Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Won't Start

Check Node dependencies:
```bash
cd frontend
npm install
```

---

## 🎯 Recommended Workflow

### Daily Development

```bash
# Start servers
npm run dev

# Open http://localhost:5173
# Click "Dev Login"
# Start coding!

# When done, press Ctrl+C
```

### After Pulling Updates

```bash
# Update dependencies
npm run install:all

# Start servers
npm run dev
```

### Clean Install

```bash
# Delete node_modules
rm -rf node_modules frontend/node_modules

# Reinstall everything
npm run install:all
```

---

## 📊 What Happens When You Run `npm run dev`

```
npm run dev
    │
    ├─→ Starts Backend (Python)
    │   └─→ http://localhost:8000
    │       ├─→ API endpoints
    │       ├─→ Video processing
    │       └─→ Database connection
    │
    └─→ Starts Frontend (Vite)
        └─→ http://localhost:5173
            ├─→ React app
            ├─→ Hot reload
            └─→ Dev mode enabled
```

Both run in the same terminal window!

---

## 🔥 Pro Tips

1. **Keep terminal open** - Don't close it while developing
2. **Watch for errors** - Check terminal output for issues
3. **Hot reload** - Frontend updates automatically on save
4. **Backend restart** - Restart servers after backend changes
5. **Use dev mode** - Click "Dev Login" for instant testing

---

## 🆚 NPM vs Batch Files

**NPM Command:**
```bash
npm run dev
```
✓ Cross-platform (Windows, Mac, Linux)
✓ One terminal window
✓ Easy to remember
✓ Stops both servers with Ctrl+C

**Batch File:**
```bash
start-dev.bat
```
✓ Windows only
✓ Two separate windows
✓ Double-click to start
✓ Close windows to stop

**Use whichever you prefer!** Both work great.

---

## 📚 More Info

- **START-HERE.md** - Getting started guide
- **DEV-MODE.md** - Dev mode features
- **SETUP.md** - Full setup instructions
- **WINDOWS-QUICK-START.txt** - Windows guide

---

**Happy coding! 🚀**
