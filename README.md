# 🎬 Clip Generator

AI-powered video clip generation using **Gemini 2.5 Flash Lite** and **OpenAI Whisper**.

Transform long videos into viral short-form clips automatically. Perfect for TikTok, Instagram Reels, and YouTube Shorts.

---

## ✨ Features

- 🤖 **AI-Powered Analysis** - Gemini 2.5 Flash Lite finds viral moments (133x cheaper than GPT-4!)
- 🎙️ **Accurate Transcription** - OpenAI Whisper with word-level timestamps
- 📱 **Multi-Format Support** - Portrait (9:16), Landscape (16:9), Square (1:1)
- ☁️ **Cloud Storage** - Cloudflare R2 / AWS S3 integration
- 💾 **PostgreSQL Database** - Neon / Railway / Supabase support
- 🎨 **Beautiful UI** - Modern React interface with dark theme
- 🚀 **Production Ready** - Deploy to Railway + Vercel in minutes

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <your-repo>
cd CLIP-GENERATOR
```

### 2. Setup Backend
```bash
setup-backend.bat
```

### 3. Configure API Key
Edit `backend/.env`:
```env
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-key
```

Get Gemini API key: https://aistudio.google.com/app/apikey

### 4. Setup Frontend
```bash
cd frontend
npm install
```

### 5. Start Application
```bash
QUICK-START.bat
```

Visit: http://localhost:5173

---

## 📖 Documentation

- **[SETUP-SUMMARY.md](SETUP-SUMMARY.md)** - Quick overview of what's included
- **[PRODUCTION-SETUP.md](PRODUCTION-SETUP.md)** - Complete production deployment guide
- **[GET-STARTED.md](GET-STARTED.md)** - Detailed getting started guide

---

## 🏗️ Architecture

### Tech Stack

**Frontend:**
- React 19
- Vite
- Lucide Icons
- Custom CSS

**Backend:**
- FastAPI (Python)
- Gemini 2.5 Flash Lite (AI)
- OpenAI Whisper (Transcription)
- MoviePy (Video Processing)
- SQLAlchemy (Database)
- Boto3 (Cloud Storage)

**Infrastructure:**
- Database: Neon PostgreSQL
- Storage: Cloudflare R2
- Backend: Railway
- Frontend: Vercel

### How It Works

```
1. User uploads video or provides YouTube URL
2. Whisper transcribes audio with timestamps
3. Gemini analyzes transcript for viral moments
4. MoviePy generates clips at identified timestamps
5. Clips uploaded to cloud storage
6. User downloads clips
```

---

## 💰 Pricing

### Development (Free Tier)
- Gemini: Free (15 req/min)
- Neon: Free (0.5GB)
- Cloudflare R2: Free (10GB)
- Railway: $5 credit
- Vercel: Free
- **Total: $0/month**

### Production (1000 videos/month)
- Gemini: $60
- Neon: Free
- Cloudflare R2: $0.75
- Railway: $15
- Vercel: Free
- **Total: ~$76/month**

**133x cheaper than using GPT-4!**

---

## 🔧 Configuration

### Required Environment Variables

```env
# Required
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-key

# Optional (for production)
DATABASE_URL=postgresql://...
STORAGE_BUCKET=your-bucket
STORAGE_ACCESS_KEY=your-key
STORAGE_SECRET_KEY=your-secret
STORAGE_ENDPOINT=https://...
STORAGE_REGION=auto
```

### Test Configuration
```bash
test-gemini.bat              # Test Gemini API
test-production-config.bat   # Test all configuration
CHECK-CONFIG.bat             # Verify setup
```

---

## 📦 What's Included

### Scripts
- `setup-backend.bat` - Install Python dependencies
- `QUICK-START.bat` - Start both servers
- `test-gemini.bat` - Test Gemini integration
- `test-production-config.bat` - Verify production config
- `CHECK-CONFIG.bat` - Check all configuration

### Backend Files
- `main.py` - FastAPI application
- `gemini_processor.py` - Gemini 2.5 Flash Lite integration
- `storage.py` - Cloud storage manager (R2/S3)
- `database.py` - PostgreSQL models
- `requirements.txt` - Python dependencies

### Frontend Files
- `src/App.jsx` - Main React component
- `src/config.js` - API configuration
- `src/CustomSelect.jsx` - Custom dropdown component

---

## 🎯 Usage

### 1. Register Account
- Create account with email/password
- Login to get JWT token

### 2. Upload Video
- **Upload File**: MP4, MOV, AVI, MKV (max 500MB)
- **YouTube URL**: Any public YouTube video
- **Direct URL**: Direct link to video file

### 3. Configure Clips
- **Number**: 3, 5, 8, or 10 clips
- **Duration**: 15s, 30s, 45s, or 60s
- **Format**: Portrait, Landscape, or Square

### 4. Generate Clips
- Click "Generate Clips"
- Wait for processing (10-15 minutes for 10-min video)
- Download individual clips

---

## 🚀 Deployment

### Deploy Backend (Railway)
```bash
# Push to GitHub
git push

# Deploy on Railway
# 1. Connect GitHub repo
# 2. Add environment variables
# 3. Deploy automatically
```

### Deploy Frontend (Vercel)
```bash
cd frontend
vercel
```

See [PRODUCTION-SETUP.md](PRODUCTION-SETUP.md) for detailed instructions.

---

## 🔍 Features in Detail

### AI-Powered Clip Selection
- Analyzes transcript for emotional peaks
- Identifies quotable moments
- Finds story arcs and climaxes
- Rates virality potential (1-10)
- Suggests best platform (TikTok/Reels/Shorts)

### Video Processing
- Automatic transcription with Whisper
- Word-level timestamp accuracy
- Multi-language support
- Automatic cropping and resizing
- Optional subtitle overlay

### Cloud Storage
- Permanent clip storage
- No temp file issues
- Fast global delivery
- Presigned download URLs
- S3-compatible (R2, S3, Spaces)

### Database
- User authentication
- Video metadata
- Job tracking
- Clip metadata
- Progress updates

---

## 🛠️ Development

### Project Structure
```
CLIP-GENERATOR/
├── backend/
│   ├── main.py
│   ├── gemini_processor.py
│   ├── storage.py
│   ├── database.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── config.js
│   │   └── CustomSelect.jsx
│   └── package.json
└── docs/
    ├── PRODUCTION-SETUP.md
    ├── SETUP-SUMMARY.md
    └── GET-STARTED.md
```

### Run Tests
```bash
# Backend
cd backend
venv\Scripts\activate
pytest

# Frontend
cd frontend
npm test
```

### Code Quality
```bash
# Python
black backend/
flake8 backend/

# JavaScript
cd frontend
npm run lint
```

---

## 📊 Performance

### Processing Time (10-minute video)
- Transcription: ~10 minutes (1x realtime)
- AI Analysis: ~3 seconds (Gemini is fast!)
- Clip Generation: ~2 minutes (5 clips)
- **Total: ~12-13 minutes**

### Optimization Tips
- Use `tiny` Whisper model for faster transcription
- Generate fewer clips (3 instead of 5)
- Use shorter clip duration (15s instead of 30s)
- Enable GPU for Whisper (10x faster)

---

## 🐛 Troubleshooting

### Backend won't start
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt --force-reinstall
```

### "Video processor not initialized"
- Check `GEMINI_API_KEY` in `.env`
- Verify key at https://aistudio.google.com/app/apikey
- Restart backend server

### Frontend can't connect
- Verify backend running on port 8000
- Check `frontend/src/config.js` API_URL
- Check browser console for CORS errors

### Database connection failed
- Verify `DATABASE_URL` format
- Check Neon project is active
- Test with: `python -c "from database import init_database; init_database('your-url')"`

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📧 Support

- **Issues**: GitHub Issues
- **Docs**: See `/docs` folder
- **Email**: your-email@example.com

---

## 🎉 Acknowledgments

- **Gemini 2.5 Flash Lite** - Google AI
- **OpenAI Whisper** - OpenAI
- **FastAPI** - Sebastián Ramírez
- **React** - Meta
- **MoviePy** - Zulko

---

## 🔗 Links

- **Gemini API**: https://aistudio.google.com/app/apikey
- **Neon Database**: https://neon.tech
- **Cloudflare R2**: https://dash.cloudflare.com/r2
- **Railway**: https://railway.app
- **Vercel**: https://vercel.com

---

**Ready to create viral clips? Get started now! 🚀**

```bash
setup-backend.bat
# Add GEMINI_API_KEY to backend/.env
QUICK-START.bat
```
