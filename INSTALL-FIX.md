# Installation Fix - psycopg2 Error

## ✅ Quick Fix (Skip Database for Now)

The database is **optional** for testing! The app works fine without it using in-memory storage.

I've already updated `requirements.txt` to skip the database packages.

**Just run:**
```bash
cd backend
pip install -r requirements.txt
```

This will install everything except the database drivers. You can add them later when needed!

---

## 🚀 Start Testing Now

```bash
# From CLIP-GENERATOR folder
npm run dev
```

Then:
1. Open http://localhost:5173
2. Click "Dev Login"
3. ~~Click "Seed Sample Data"~~ (requires database)
4. Use "Generate Clips" to create real clips!

**Note:** Without a database, you can't use "Seed Sample Data", but you can still:
- Generate real clips from videos
- Download clips
- Test the UI

Your clips will be stored in memory (lost when you restart the server).

---

## 📊 When You Need Database (Later)

The database is only needed for:
- Persistent storage (clips saved between restarts)
- "Seed Sample Data" feature
- Production deployment
- Analytics tracking over time

### Option 1: Use Free PostgreSQL (Recommended)

**Neon (Easiest):**
1. Go to https://neon.tech
2. Sign up (free)
3. Create a database
4. Copy connection string
5. Add to `backend/.env`:
   ```
   DATABASE_URL=postgresql://user:pass@host/db
   ```
6. Install database packages:
   ```bash
   pip install sqlalchemy psycopg[binary]
   ```

### Option 2: Install psycopg2 on Windows

If you really want to install psycopg2-binary:

**Method 1 - Use newer psycopg:**
```bash
pip install "psycopg[binary]"
pip install sqlalchemy==2.0.23
```

**Method 2 - Download pre-built wheel:**
1. Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#psycopg
2. Download the wheel for your Python version (e.g., cp313 = Python 3.13)
3. Install: `pip install psycopg2_binary-2.9.9-cp313-cp313-win_amd64.whl`

**Method 3 - Install PostgreSQL locally:**
1. Install PostgreSQL: https://www.postgresql.org/download/windows/
2. This includes pg_config needed to build psycopg2
3. Then: `pip install psycopg2-binary`

---

## 🎯 Recommended Workflow

### For Testing (Now)
```bash
# No database needed!
cd backend
pip install -r requirements.txt
cd ..
npm run dev
```

### For Production (Later)
```bash
# Add database
pip install sqlalchemy psycopg[binary]

# Configure DATABASE_URL in .env
# Then restart server
```

---

## ❓ FAQ

**Q: Can I use the app without a database?**
A: Yes! It works fine for testing. Clips are stored in memory.

**Q: Will I lose my clips?**
A: Without a database, yes - clips are lost when you restart the server.

**Q: When should I add a database?**
A: When you want to:
- Keep clips between restarts
- Use the "Seed Sample Data" feature
- Deploy to production
- Track analytics over time

**Q: What's the easiest database option?**
A: Neon.tech - free PostgreSQL, no installation needed, just copy the connection string.

**Q: Can I add the database later?**
A: Absolutely! Just install the packages and add DATABASE_URL to .env. No code changes needed.

---

## 🔧 Current Status

✅ Core features work without database:
- Video upload
- YouTube URL processing
- AI clip generation
- Clip download
- Dev login

❌ Features that need database:
- Seed sample data
- Persistent clip storage
- Analytics dashboard (with saved data)
- Clips library (with saved clips)

**Start testing now, add database when you need it!**

---

## 📝 Summary

1. **For now:** Skip database, test with in-memory storage
2. **Later:** Add free Neon database when you want persistence
3. **No rush:** Everything works for testing without it!

```bash
# Just run this and start testing:
npm run dev
```

🎉 **You're ready to go!**
