# 🚀 Setup Instructions for Your Friend

## Quick Setup (3 Steps)

### 1. Navigate to project folder
```bash
cd CLIP-GENERATOR
```

### 2. Install all dependencies
```bash
npm run install:all
```

### 3. Start the app
```bash
npm run dev
```

That's it! Open http://localhost:5173

---

## If that doesn't work, try manual install:

```bash
cd CLIP-GENERATOR
npm install
cd frontend
npm install
cd ..
npm run dev
```

---

## Common Issues

**"concurrently not found"**
- Run `npm install` in the CLIP-GENERATOR folder first

**"Cannot find module 'react'"**
- Run `npm install` in the frontend folder

**Backend errors**
- Make sure Python is installed
- Run `cd backend && pip install -r requirements.txt`

---

## Need the backend too?

If they want the full app with backend:

```bash
cd CLIP-GENERATOR
npm run install:all
npm run dev
```

This installs:
- Root dependencies (concurrently)
- Frontend dependencies (React, Vite)
- Backend dependencies (FastAPI, etc.)
