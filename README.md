# ClipGen - AI-Powered Viral Clip Marketplace

**Turn any video into viral clips. Get paid.**

ClipGen is a two-sided marketplace where content creators and brands post campaigns, and skilled clippers use AI to generate viral short-form content. Clippers earn money based on performance with tiered revenue splits (70/30 to 85/15).

---

## 🎯 Mission

Democratize viral content creation by combining AI automation with human creativity. Enable anyone to earn money creating clips while helping creators and brands maximize their reach on TikTok, YouTube Shorts, and Instagram Reels.

---

## 🏗️ Architecture

### Tech Stack

**Backend (Python)**
- FastAPI - High-performance async API
- PostgreSQL - Primary database (SQLAlchemy ORM)
- Redis + RQ - Job queue for video processing
- Gemini 2.5 Flash Lite - AI clip analysis (133x cheaper than GPT-4)
- Whisper - Speech-to-text transcription
- FFmpeg - Video processing and audio analysis
- S3-compatible storage - Cloudflare R2, AWS S3, DigitalOcean Spaces

**Frontend (React)**
- React 18 + Vite - Fast development and builds
- Lucide Icons - Clean, modern iconography
- CSS Variables - Themeable design system

**Integrations**
- YouTube Data API v3 - Auto-upload with tracking
- Stripe Connect (planned) - Automated payments

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  Dashboard | Marketplace | Clip Generator | Analytics       │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────┴────────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Auth   │  │Marketplace│  │ YouTube  │  │  Video   │   │
│  │  Module  │  │    API    │  │   API    │  │Processor │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼─────┐    ┌────▼─────┐    ┌────▼─────┐
   │PostgreSQL│    │  Redis   │    │    S3    │
   │ Database │    │  Queue   │    │ Storage  │
   └──────────┘    └──────────┘    └──────────┘
```

### Data Flow

**Self-Service Flow:**
```
User → Upload Video → AI Processing → Generate Clips → Download
```

**Marketplace Flow:**
```
Client → Create Campaign → Post to Marketplace
                              ↓
Clipper → Browse → Claim Job → Generate Clips
                              ↓
Clipper → Submit → Upload to YouTube (auto-tracked)
                              ↓
Client → Review → Approve/Reject
                              ↓
Clipper → Request Payout → Receive Payment
                              ↓
Daily Cron → Sync Views → Calculate Bonuses
```

---

## 💰 Revenue Model

### Tiered Revenue Splits

Clippers earn more as they prove their skills:

| Tier | Split | Requirements |
|------|-------|--------------|
| 🥉 Bronze | 70/30 | New users (default) |
| 🥈 Silver | 75/25 | 10+ approved clips OR 100k+ views |
| 🥇 Gold | 80/20 | 50+ approved clips OR 500k+ views |
| 💎 Platinum | 85/15 | 100+ approved clips OR 1M+ views |

### Performance Bonuses

Viral clips earn automatic bonuses:
- 100k views = 20% bonus
- 500k views = 50% bonus
- 1M views = 100% bonus
- 5M views = 200% bonus

### Platform Revenue Streams

1. **Revenue Share** - 15-30% per clip (based on clipper tier)
2. **Marketplace Fee** - 5-10% on campaign budgets (future)
3. **Client Subscriptions** - Tiered plans (future)
4. **Premium AI Tools** - Advanced features for clippers (future)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL (or use Neon.tech free tier)
- FFmpeg installed

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run server
python main.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

### Environment Variables

**Backend (.env):**
```bash
SECRET_KEY=<generate-with-secrets.token_urlsafe(32)>
GEMINI_API_KEY=<from-google-ai-studio>
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DISABLE_AUTH=false  # true for local dev only

# Optional
STORAGE_BUCKET=<s3-bucket-name>
STORAGE_ACCESS_KEY=<aws-access-key>
STORAGE_SECRET_KEY=<aws-secret-key>
```

**Frontend (.env):**
```bash
VITE_API_URL=http://localhost:8000
```

---

## 📁 Project Structure

```
CLIP-GENERATOR/
├── backend/
│   ├── main.py                 # FastAPI app, core routes
│   ├── auth.py                 # Authentication module
│   ├── database.py             # SQLAlchemy models
│   ├── marketplace.py          # Marketplace API
│   ├── youtube_integration.py  # YouTube upload & tracking
│   ├── gemini_processor.py     # AI clip generation
│   ├── storage.py              # S3 storage handler
│   ├── ffmpeg_helpers.py       # Audio analysis
│   ├── scene_detection.py      # Camera cut detection
│   ├── emotion_detector.py     # Hype moment detection
│   ├── subtitles.py            # SRT/VTT generation
│   └── cron_sync_views.py      # Daily view sync job
│
├── frontend/
│   └── src/
│       ├── App.jsx             # Main app with routing
│       ├── Dashboard.jsx       # Analytics dashboard
│       ├── Marketplace.jsx     # Browse campaigns
│       ├── CreateCampaign.jsx  # Campaign creation
│       ├── SubmitJob.jsx       # Job submission
│       └── ClipsLibrary.jsx    # Clip history
│
└── README.md
```

---

## 🔑 Key Features

### For Clippers
- ✅ AI-powered clip generation (Gemini + Whisper)
- ✅ Browse available campaigns
- ✅ Tiered earnings (70-85% revenue share)
- ✅ Performance bonuses for viral clips
- ✅ Auto-upload to YouTube with tracking
- ✅ Portfolio and rating system

### For Clients
- ✅ Post campaigns with requirements
- ✅ Review and approve submissions
- ✅ Track performance analytics
- ✅ Pay per clip or bulk pricing
- ✅ Quality ratings and feedback

### AI Processing
- ✅ Automatic transcription (Whisper)
- ✅ Viral moment detection (Gemini 2.5)
- ✅ Audio energy analysis
- ✅ Scene change detection
- ✅ Emotion/hype detection
- ✅ Auto-generated subtitles (SRT/VTT)

---

## 🧪 Testing

```bash
# Backend tests (coming soon)
cd backend
pytest

# Frontend tests (coming soon)
cd frontend
npm test
```

---

## 📊 Database Schema

### Core Tables
- `users` - User accounts with marketplace roles
- `campaigns` - Client job postings
- `marketplace_jobs` - Job assignments and tracking
- `clips` - Generated clips with performance data
- `payouts` - Payment tracking

### Relationships
```
users (1) ──→ (N) campaigns (client posts jobs)
users (1) ──→ (N) marketplace_jobs (clipper claims jobs)
campaigns (1) ──→ (N) marketplace_jobs
marketplace_jobs (1) ──→ (1) clips
users (1) ──→ (N) payouts
```

---

## 🔐 Security

- JWT token authentication
- Bcrypt password hashing
- Rate limiting on all endpoints
- CORS configuration
- Input validation with Pydantic
- SQL injection protection (SQLAlchemy ORM)

---

## 🚢 Deployment

### Recommended Stack
- **Backend:** Railway or Render
- **Frontend:** Vercel or Netlify
- **Database:** Neon.tech (PostgreSQL)
- **Storage:** Cloudflare R2 or AWS S3
- **Queue:** Upstash Redis

### Deploy Checklist
1. Set up PostgreSQL database
2. Configure environment variables
3. Deploy backend API
4. Deploy frontend app
5. Set up cron job for view sync
6. Configure YouTube OAuth (optional)

---

## 📈 Roadmap

### MVP (Current)
- [x] AI clip generation
- [x] Marketplace system
- [x] YouTube integration
- [x] Tiered revenue splits
- [x] Performance bonuses

### v2.0
- [ ] Stripe Connect payments
- [ ] Email notifications
- [ ] Advanced analytics
- [ ] Multi-platform support (TikTok, Instagram)
- [ ] Referral system

### v3.0
- [ ] White-label for agencies
- [ ] Team accounts
- [ ] API for integrations
- [ ] Mobile apps

---

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

---

## 📄 License

Proprietary - All rights reserved

---

## 🆘 Support

For issues or questions:
- Create an issue on GitHub
- Email: support@clipgen.ai (placeholder)

---

**Built with ❤️ using AI and human creativity**
