<p align="center">
  <img src="frontend/public/logos/logo-full.svg" alt="ClipGen Logo" width="400"/>
</p>

<h1 align="center">🎬 ClipGen</h1>

<p align="center">
  <strong>AI-Powered Viral Clip Marketplace</strong>
</p>

<p align="center">
  <em>Turn any video into viral clips. Get paid. 💰</em>
</p>

<p align="center">
  <a href="#-quick-start"><img src="https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge" alt="Quick Start"/></a>
  <a href="#-features"><img src="https://img.shields.io/badge/Features-green?style=for-the-badge" alt="Features"/></a>
  <a href="#-deployment"><img src="https://img.shields.io/badge/Deploy-orange?style=for-the-badge" alt="Deploy"/></a>
  <a href="#-documentation"><img src="https://img.shields.io/badge/Docs-purple?style=for-the-badge" alt="Docs"/></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black" alt="React"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Gemini%20AI-8E75B2?style=flat-square&logo=google&logoColor=white" alt="Gemini"/>
</p>

---

## 🌟 What is ClipGen?

ClipGen is a **two-sided marketplace** where content creators and brands post campaigns, and skilled clippers use AI to generate viral short-form content. 

> 🎯 **Mission:** Democratize viral content creation by combining AI automation with human creativity.

### 💡 How It Works

```
📹 Upload Video  →  🤖 AI Analysis  →  ✂️ Generate Clips  →  📊 Track Performance  →  💵 Get Paid
```

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎬 For Clippers
- ✅ AI-powered clip generation
- ✅ Browse available campaigns
- ✅ Tiered earnings (70-85% split)
- ✅ Performance bonuses for viral clips
- ✅ Auto-upload to YouTube
- ✅ Portfolio & rating system

</td>
<td width="50%">

### 🏢 For Clients
- ✅ Post campaigns with requirements
- ✅ Review and approve submissions
- ✅ Track performance analytics
- ✅ Pay per clip or bulk pricing
- ✅ Quality ratings and feedback

</td>
</tr>
</table>

### 🤖 AI Processing Pipeline

| Feature | Technology | Status |
|---------|------------|--------|
| 🎙️ Transcription | Whisper / Faster-Whisper | ✅ Ready |
| 🔥 Viral Detection | Gemini 2.5 Flash Lite | ✅ Ready |
| 🎵 Audio Analysis | FFmpeg | ✅ Ready |
| 🎬 Scene Detection | OpenCV | ✅ Ready |
| 😄 Emotion Detection | Custom ML | ✅ Ready |
| 📝 Auto Subtitles | SRT/VTT Generator | ✅ Ready |

---

## 💰 Revenue Model

### 🏆 Tiered Revenue Splits

Clippers earn more as they prove their skills:

| Tier | Split | Requirements |
|:----:|:-----:|:-------------|
| 🥉 **Bronze** | 70/30 | New users (default) |
| 🥈 **Silver** | 75/25 | 10+ clips OR 100k+ views |
| 🥇 **Gold** | 80/20 | 50+ clips OR 500k+ views |
| 💎 **Platinum** | 85/15 | 100+ clips OR 1M+ views |

### 🚀 Performance Bonuses

| Views | Bonus |
|:-----:|:-----:|
| 100k | +20% 🔥 |
| 500k | +50% 🔥🔥 |
| 1M | +100% 🔥🔥🔥 |
| 5M | +200% 💥 |

---

## 🚀 Quick Start

### 📋 Prerequisites

```
✅ Python 3.10+
✅ Node.js 18+
✅ FFmpeg installed
✅ PostgreSQL (or Neon.tech free tier)
```

### ⚡ One-Command Setup (Windows)

```bash
# Clone and run
git clone https://github.com/sourdieseleyez/CLIP-GENERATOR.git
cd CLIP-GENERATOR
QUICK-START.bat
```

### 🔧 Manual Setup

<details>
<summary><strong>Backend Setup</strong></summary>

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run server
python main.py
```

</details>

<details>
<summary><strong>Frontend Setup</strong></summary>

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

</details>

### 🔑 Environment Variables

<details>
<summary><strong>Backend (.env)</strong></summary>

```env
# Required
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Storage (Optional)
STORAGE_BUCKET=your-bucket
STORAGE_ACCESS_KEY=your-key
STORAGE_SECRET_KEY=your-secret
```

</details>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    🖥️ Frontend (React)                       │
│     Dashboard │ Marketplace │ Generator │ Analytics         │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────┴────────────────────────────────────┐
│                    ⚡ Backend (FastAPI)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  🔐 Auth │  │🏪 Market │  │📺 YouTube│  │🎬 Video  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼─────┐    ┌────▼─────┐    ┌────▼─────┐
   │🐘 Postgres│    │⚡ Redis  │    │☁️ S3     │
   │ Database │    │  Queue   │    │ Storage  │
   └──────────┘    └──────────┘    └──────────┘
```

### 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, Vite, Lucide Icons |
| **Backend** | FastAPI, Python 3.10+ |
| **Database** | PostgreSQL, SQLAlchemy |
| **AI** | Gemini 2.5 Flash Lite, Whisper |
| **Queue** | Redis + RQ |
| **Storage** | S3 / Cloudflare R2 |
| **Video** | FFmpeg |

---

## 📁 Project Structure

```
📦 CLIP-GENERATOR
├── 🐍 backend/
│   ├── main.py              # FastAPI app
│   ├── auth.py              # JWT authentication
│   ├── database.py          # SQLAlchemy models
│   ├── marketplace.py       # Marketplace API
│   ├── gemini_processor.py  # AI clip generation
│   ├── youtube_integration.py
│   └── storage.py           # S3 handler
│
├── ⚛️ frontend/
│   └── src/
│       ├── App.jsx          # Main router
│       ├── Dashboard.jsx    # Analytics
│       ├── Marketplace.jsx  # Browse jobs
│       ├── ClipsLibrary.jsx # Clip history
│       └── ...
│
├── 🐳 Dockerfile
├── 🚀 fly.toml
└── 📖 README.md
```

---

## 🔐 Security

| Feature | Implementation |
|---------|----------------|
| 🔑 Authentication | JWT tokens with expiration |
| 🔒 Passwords | Bcrypt hashing |
| 🚦 Rate Limiting | slowapi on all endpoints |
| 🌐 CORS | Configurable origins |
| ✅ Validation | Pydantic models |
| 🛡️ SQL Injection | SQLAlchemy ORM |

---

## 🚢 Deployment

### ☁️ Recommended Stack

| Service | Provider | Cost |
|---------|----------|------|
| **Backend** | Railway / Render | ~$15/mo |
| **Frontend** | Vercel / Netlify | Free |
| **Database** | Neon.tech | Free tier |
| **Storage** | Cloudflare R2 | Free tier |
| **Queue** | Upstash Redis | Free tier |

### 💵 Cost Estimate

| Scale | Monthly Cost |
|-------|--------------|
| 🧪 Development | **$0** |
| 🚀 100 videos/mo | **~$10** |
| 📈 1000 videos/mo | **~$75** |
| 🏢 10000 videos/mo | **~$750** |

---

## 📈 Roadmap

### ✅ MVP (Current)
- [x] AI clip generation
- [x] Marketplace system
- [x] YouTube integration
- [x] Tiered revenue splits
- [x] Performance bonuses
- [x] OAuth (Google, GitHub)

### 🔜 v2.0
- [ ] Stripe Connect payments
- [ ] Email notifications
- [ ] Advanced analytics
- [ ] TikTok/Instagram upload
- [ ] Referral system

### 🔮 v3.0
- [ ] White-label for agencies
- [ ] Team accounts
- [ ] Public API
- [ ] Mobile apps

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [🚀 Quick Start](QUICK-START-DEV.txt) | Get running in 5 minutes |
| [⚙️ Production Setup](PRODUCTION-SETUP.md) | Deploy to production |
| [🐳 Docker Deploy](FLY-DEPLOYMENT.md) | Fly.io deployment |
| [📊 Features](FEATURES-SUMMARY.md) | Full feature list |
| [🗺️ Roadmap](MVP-ROADMAP.md) | Development roadmap |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Proprietary - All rights reserved

---

## 🆘 Support

- 📧 Email: support@clipgen.ai
- 🐛 Issues: [GitHub Issues](https://github.com/sourdieseleyez/CLIP-GENERATOR/issues)
- 💬 Discord: Coming soon

---

<p align="center">
  <strong>Built with ❤️ using AI and human creativity</strong>
</p>

<p align="center">
  <img src="frontend/public/logos/logo-mark.svg" alt="ClipGen" width="50"/>
</p>

<p align="center">
  <sub>© 2025 ClipGen. All rights reserved.</sub>
</p>
