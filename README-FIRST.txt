╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                        🎬 CLIP GENERATOR 🎬                              ║
║                                                                          ║
║              AI-Powered Video Clip Generation & Analytics                ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝


🚀 SUPER QUICK START
══════════════════════════════════════════════════════════════════════════

  1. npm run install:all
  2. npm run dev
  3. Open http://localhost:5173
  4. Click "Dev Login" → "Seed Sample Data"
  5. Explore!


📚 WHICH GUIDE TO READ?
══════════════════════════════════════════════════════════════════════════

  🎯 QUICKEST-START.txt          ← 3 commands, that's it!
  
  📖 START-HERE.md               ← Full getting started guide
  
  💻 NPM-COMMANDS.md             ← All npm commands explained
  
  🪟 WINDOWS-QUICK-START.txt     ← Windows-specific guide
  
  🎨 VISUAL-GUIDE.txt            ← See the UI flow
  
  🔧 DEV-MODE.md                 ← Dev mode features
  
  ⚙️  SETUP.md                    ← Full setup & configuration
  
  🚀 PRODUCTION-SETUP.md         ← Deploy to production


🎯 WHAT THIS APP DOES
══════════════════════════════════════════════════════════════════════════

  ✓ Upload videos or paste YouTube URLs
  ✓ AI finds viral moments automatically
  ✓ Generate clips with captions
  ✓ Track views and revenue per clip
  ✓ Analytics dashboard
  ✓ Clips library with search/filter
  ✓ Platform performance tracking


💡 KEY FEATURES
══════════════════════════════════════════════════════════════════════════

  🤖 AI-Powered
     • Gemini 2.5 Flash Lite (133x cheaper than GPT-4!)
     • Finds viral moments automatically
     • Generates hooks and captions

  📊 Analytics Dashboard
     • Track views and revenue
     • Platform breakdown (TikTok, YouTube, Instagram)
     • Top performing clips
     • Category insights

  📚 Clips Library
     • Search and filter clips
     • Edit analytics
     • Download clips
     • Sort by performance

  🔧 Dev Mode
     • One-click login
     • Sample data generator
     • No setup required for testing


🎮 TWO WAYS TO START
══════════════════════════════════════════════════════════════════════════

  METHOD 1: NPM (Recommended)
  ────────────────────────────────────────────────────────────────────────
    npm run dev
    
    ✓ Cross-platform
    ✓ One terminal
    ✓ Easy to remember
    ✓ Ctrl+C to stop


  METHOD 2: Batch File (Windows)
  ────────────────────────────────────────────────────────────────────────
    Double-click: start-dev.bat
    
    ✓ No typing needed
    ✓ Two separate windows
    ✓ Close windows to stop


📦 FIRST TIME SETUP
══════════════════════════════════════════════════════════════════════════

  1. Install Dependencies
     ─────────────────────────────────────────────────────────────────────
     npm run install:all

  2. Configure Backend (Optional for dev mode)
     ─────────────────────────────────────────────────────────────────────
     Create backend/.env:
     
       SECRET_KEY=your-secret-key
       GEMINI_API_KEY=your-gemini-key
       ENVIRONMENT=development

     Get Gemini key: https://aistudio.google.com/app/apikey

  3. Start Servers
     ─────────────────────────────────────────────────────────────────────
     npm run dev

  4. Open Browser
     ─────────────────────────────────────────────────────────────────────
     http://localhost:5173


🎨 DEV MODE FEATURES
══════════════════════════════════════════════════════════════════════════

  When you open the app, you'll see:
  
  🟣 Purple "Development Mode" banner at top
  🟣 "Dev Login" button in sidebar
  🟣 "Seed Sample Data" button (after login)
  
  This lets you test everything without:
  • Creating an account
  • Uploading videos
  • Configuring database
  • Setting up storage


📊 SAMPLE DATA
══════════════════════════════════════════════════════════════════════════

  After clicking "Seed Sample Data", you get:
  
  • 10 realistic clips
  • 750K total views
  • $37.42 total revenue
  • Mixed platforms (TikTok, YouTube, Instagram)
  • Various categories (humor, educational, controversial, etc.)
  • Virality scores 5-9/10


🛠️ TECH STACK
══════════════════════════════════════════════════════════════════════════

  Backend:
    • Python + FastAPI
    • Gemini 2.5 Flash Lite (AI)
    • Whisper (transcription)
    • MoviePy (video processing)
    • PostgreSQL (database)
    • S3-compatible storage

  Frontend:
    • React + Vite
    • Modern CSS
    • Responsive design


💰 COST BREAKDOWN
══════════════════════════════════════════════════════════════════════════

  Development (Free Tier):
    • Gemini API: Free quota
    • Database: Neon free tier
    • Storage: Cloudflare R2 free tier
    • Total: $0/month

  Production (1000 videos/month):
    • Gemini API: ~$5-10
    • Database: ~$5-10
    • Storage: ~$5-10
    • Hosting: ~$5-10
    • Total: ~$25-40/month


📁 PROJECT STRUCTURE
══════════════════════════════════════════════════════════════════════════

  CLIP-GENERATOR/
  ├── 🚀 start-dev.bat          ← Double-click to start
  ├── 📄 package.json            ← npm scripts
  │
  ├── backend/
  │   ├── main.py               ← API server
  │   ├── database.py           ← Database models
  │   ├── gemini_processor.py   ← AI processing
  │   └── .env                  ← Your config
  │
  └── frontend/
      ├── src/
      │   ├── App.jsx           ← Main app
      │   ├── Dashboard.jsx     ← Analytics
      │   └── ClipsLibrary.jsx  ← Clips management
      └── package.json


🐛 TROUBLESHOOTING
══════════════════════════════════════════════════════════════════════════

  "npm not found"
    → Install Node.js: https://nodejs.org/

  "python not found"
    → Install Python: https://www.python.org/downloads/

  "Port already in use"
    → Close other apps or restart computer

  "Dev Login button not showing"
    → Make sure you're running npm run dev (not build)

  "Seed Data fails"
    → Database must be configured (see SETUP.md)

  More help: See NPM-COMMANDS.md troubleshooting section


🎯 NEXT STEPS
══════════════════════════════════════════════════════════════════════════

  After exploring with dev mode:

  1. Configure Real Services
     • Database (Neon, Railway, Supabase)
     • Storage (Cloudflare R2, AWS S3)
     • Get Gemini API key

  2. Generate Real Clips
     • Upload your videos
     • Or use YouTube URLs
     • AI finds best moments

  3. Post to Platforms
     • Download generated clips
     • Upload to TikTok, YouTube, Instagram

  4. Track Performance
     • Update views in Clips Library
     • Monitor revenue
     • Optimize strategy


📞 SUPPORT
══════════════════════════════════════════════════════════════════════════

  Documentation:
    • All guides in this folder
    • Comments in code
    • .env.example for config

  Common Issues:
    • Check terminal for errors
    • Read NPM-COMMANDS.md
    • See SETUP.md for full setup


╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                         READY TO START? 🚀                               ║
║                                                                          ║
║                         npm run install:all                              ║
║                         npm run dev                                      ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
