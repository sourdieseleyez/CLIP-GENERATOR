# 🚀 Quick Start - Clip Generator

## Fastest Way to Test

**Option 1 - NPM Command (Recommended):**
```bash
npm run dev
```
Starts both servers in one terminal!

**Option 2 - Windows Batch File:**
Double-click `start-dev.bat`
Opens both servers in separate windows

Then in your browser:
1. Open http://localhost:5173
2. Click **"Dev Login"** (purple button in sidebar)
3. Click **"Seed Sample Data"** (purple button)
4. Explore **Dashboard** and **Clips Library**!

---

## What You'll See

### Dashboard
- Total clips, views, and revenue stats
- Platform performance (TikTok, YouTube, Instagram)
- Top performing clips
- Category analytics

### Clips Library
- Searchable table of all clips
- Filter by platform and category
- Sort by views, revenue, or virality
- Edit analytics for each clip
- Download clips

### Generate Clips
- Upload videos or paste YouTube URLs
- AI finds viral moments
- Generate clips automatically

---

## Manual Start (if batch file doesn't work)

**Terminal 1 - Backend:**
```powershell
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

---

## First Time Setup

If you haven't installed dependencies yet:

**Install Everything (One Command):**
```bash
npm run install:all
```

**Or Install Separately:**

Backend:
```bash
cd backend
pip install -r requirements.txt
```

Frontend:
```bash
cd frontend
npm install
```

---

## Configuration

Create `backend/.env` file (copy from `.env.example`):

```bash
# Minimum required for dev mode
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
ENVIRONMENT=development

# Optional (for full features)
DATABASE_URL=your-postgresql-url
STORAGE_BUCKET=your-bucket-name
STORAGE_ACCESS_KEY=your-access-key
STORAGE_SECRET_KEY=your-secret-key
```

Get Gemini API key: https://aistudio.google.com/app/apikey (free!)

---

## Documentation

- **QUICK-START-DEV.txt** - Quick reference card
- **DEV-MODE.md** - Detailed dev mode guide
- **FEATURES-SUMMARY.md** - All features overview
- **ANALYTICS-UPDATE.md** - Analytics features
- **SETUP.md** - Full setup instructions
- **PRODUCTION-SETUP.md** - Production deployment

---

## Troubleshooting

**Backend won't start:**
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.8+)
- Verify .env file exists in backend folder

**Frontend won't start:**
- Install dependencies: `npm install`
- Check Node version: `node --version` (need 16+)
- Try: `npm cache clean --force` then `npm install`

**Dev Login button not showing:**
- Make sure you're running `npm run dev` (not `npm run build`)
- Check browser console for errors
- Verify frontend is running on http://localhost:5173

**Seed Data fails:**
- Database must be configured (PostgreSQL)
- Check backend logs for errors
- Make sure you clicked "Dev Login" first

---

## Need Help?

Check the documentation files or backend logs for error messages.

**Common Issues:**
- Missing dependencies → Run install commands above
- Port already in use → Close other apps using ports 8000 or 5173
- Database errors → Configure DATABASE_URL in .env

---

## What's Next?

After testing with dev mode:
1. Configure real database (Neon, Railway, Supabase)
2. Set up cloud storage (Cloudflare R2, AWS S3)
3. Deploy to production (Railway, Vercel, etc.)

See **PRODUCTION-SETUP.md** for deployment guide.

---

**Happy clipping! 🎬✨**
