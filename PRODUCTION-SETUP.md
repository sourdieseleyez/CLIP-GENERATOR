# 🚀 Production Setup Guide

Complete guide to deploy your Clip Generator to production with database and cloud storage.

## 📋 Overview

**What You'll Set Up:**
1. **Database**: Neon PostgreSQL (free tier available)
2. **Storage**: Cloudflare R2 (free tier available)
3. **Backend**: Railway (easy deployment)
4. **Frontend**: Vercel/Netlify (static hosting)

**Total Cost:**
- Development: **$0/month** (all free tiers)
- Production (1000 videos/month): **~$25-40/month**

---

## 1️⃣ Database Setup (Neon PostgreSQL)

### Why Neon?
- ✅ **Free tier**: 0.5GB storage, perfect for starting
- ✅ **Serverless**: Auto-scales, no management needed
- ✅ **Fast**: Built for modern apps
- ✅ **Easy**: One-click setup

### Setup Steps

**1. Create Neon Account**
- Go to https://neon.tech
- Sign up with GitHub/Google
- Create a new project

**2. Get Connection String**
```
Project Dashboard → Connection Details → Connection string
```

Copy the connection string, it looks like:
```
postgresql://username:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**3. Add to .env**
```env
DATABASE_URL=postgresql://username:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**4. Test Connection**
```bash
cd backend
venv\Scripts\activate
python -c "from database import init_database; init_database('your-connection-string')"
```

### Neon Pricing
- **Free**: 0.5GB storage, 1 project
- **Pro**: $19/month - 10GB storage, unlimited projects
- **Scale**: Custom pricing

For 1000 videos/month: **Free tier is enough!**

---

## 2️⃣ Cloud Storage Setup (Cloudflare R2)

### Why Cloudflare R2?
- ✅ **Free tier**: 10GB storage, 1M requests/month
- ✅ **Zero egress fees**: Huge cost savings vs S3
- ✅ **S3-compatible**: Works with existing tools
- ✅ **Fast**: Cloudflare's global network

### Setup Steps

**1. Create Cloudflare Account**
- Go to https://dash.cloudflare.com
- Sign up (free)
- Navigate to R2 section

**2. Create R2 Bucket**
```
R2 → Create bucket
Name: clip-generator-videos (or your choice)
Location: Automatic
```

**3. Create API Token**
```
R2 → Manage R2 API Tokens → Create API Token
Name: clip-generator-api
Permissions: Object Read & Write
TTL: Forever (or set expiration)
```

Copy the credentials:
- Access Key ID
- Secret Access Key
- Endpoint URL (looks like: https://abc123.r2.cloudflarestorage.com)

**4. Add to .env**
```env
STORAGE_BUCKET=clip-generator-videos
STORAGE_ACCESS_KEY=your-access-key-id
STORAGE_SECRET_KEY=your-secret-access-key
STORAGE_ENDPOINT=https://abc123.r2.cloudflarestorage.com
STORAGE_REGION=auto
```

**5. Make Bucket Public (Optional)**
```
Bucket Settings → Public Access → Allow
```
This allows direct downloads without presigned URLs.

### R2 Pricing
- **Free**: 10GB storage, 1M Class A requests, 10M Class B requests/month
- **Paid**: $0.015/GB storage, $4.50/million Class A requests
- **Egress**: $0 (FREE!)

For 1000 videos/month (~50GB): **~$0.75/month**

### Alternative: AWS S3
If you prefer AWS S3:
```env
STORAGE_BUCKET=your-s3-bucket-name
STORAGE_ACCESS_KEY=your-aws-access-key
STORAGE_SECRET_KEY=your-aws-secret-key
STORAGE_ENDPOINT=  # Leave empty for S3
STORAGE_REGION=us-east-1  # Your AWS region
```

**S3 Pricing** (more expensive):
- Storage: $0.023/GB
- Egress: $0.09/GB (expensive!)
- For 1000 videos: **~$10-15/month**

---

## 3️⃣ Backend Deployment (Railway)

### Why Railway?
- ✅ **Easy deployment**: Git push to deploy
- ✅ **Built-in PostgreSQL**: Can use instead of Neon
- ✅ **Auto-scaling**: Handles traffic spikes
- ✅ **$5 free credit**: Perfect for testing

### Setup Steps

**1. Create Railway Account**
- Go to https://railway.app
- Sign up with GitHub
- Get $5 free credit

**2. Create New Project**
```
New Project → Deploy from GitHub repo
Select your repository
```

**3. Configure Environment Variables**
```
Project → Variables → Add Variables
```

Add all your .env variables:
```
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-key
DATABASE_URL=your-neon-connection-string
STORAGE_BUCKET=your-bucket-name
STORAGE_ACCESS_KEY=your-access-key
STORAGE_SECRET_KEY=your-secret-key
STORAGE_ENDPOINT=your-r2-endpoint
STORAGE_REGION=auto
```

**4. Configure Build**
```
Settings → Build Command: pip install -r backend/requirements.txt
Settings → Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**5. Deploy**
Railway will auto-deploy on every git push!

**6. Get Your API URL**
```
Settings → Domains → Generate Domain
```
You'll get: `https://your-app.railway.app`

### Railway Pricing
- **Free**: $5 credit/month
- **Hobby**: $5/month + usage
- **Pro**: $20/month + usage

For 1000 videos/month: **~$10-20/month**

### Alternative: Render
Similar to Railway, also has free tier:
- Go to https://render.com
- Deploy as Web Service
- Free tier: 750 hours/month

---

## 4️⃣ Frontend Deployment (Vercel)

### Setup Steps

**1. Update API URL**
Edit `frontend/src/config.js`:
```javascript
export const API_URL = import.meta.env.VITE_API_URL || 'https://your-app.railway.app';
```

Or create `frontend/.env.production`:
```env
VITE_API_URL=https://your-app.railway.app
```

**2. Deploy to Vercel**
```bash
cd frontend
npm install -g vercel
vercel
```

Follow prompts:
- Link to your project
- Set build command: `npm run build`
- Set output directory: `dist`

**3. Configure CORS**
Update `backend/main.py`:
```python
allow_origins=[
    "http://localhost:5173",
    "https://your-app.vercel.app",  # Add your Vercel domain
]
```

Redeploy backend to Railway (git push).

### Vercel Pricing
- **Free**: Unlimited deployments, 100GB bandwidth
- **Pro**: $20/month - More bandwidth

For most use cases: **Free tier is enough!**

### Alternative: Netlify
```bash
cd frontend
npm run build
netlify deploy --prod --dir=dist
```

---

## 5️⃣ Complete .env Configuration

### Backend (.env)

```env
# ============================================
# REQUIRED
# ============================================
SECRET_KEY=your-generated-secret-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# ============================================
# DATABASE (Neon PostgreSQL)
# ============================================
DATABASE_URL=postgresql://user:pass@host.neon.tech/db?sslmode=require

# ============================================
# STORAGE (Cloudflare R2)
# ============================================
STORAGE_BUCKET=clip-generator-videos
STORAGE_ACCESS_KEY=your-r2-access-key
STORAGE_SECRET_KEY=your-r2-secret-key
STORAGE_ENDPOINT=https://abc123.r2.cloudflarestorage.com
STORAGE_REGION=auto
```

### Frontend (.env.production)

```env
VITE_API_URL=https://your-app.railway.app
```

---

## 6️⃣ Testing Production Setup

### Test Database Connection
```bash
cd backend
venv\Scripts\activate
python -c "from database import init_database; init_database('your-db-url'); print('✓ Database connected')"
```

### Test Storage Connection
```bash
python -c "from storage import init_storage; s = init_storage('bucket', 'key', 'secret', 'endpoint'); print('✓ Storage connected' if s.enabled else '✗ Storage failed')"
```

### Test Full Backend
```bash
python main.py
```

Visit http://localhost:8000/health

Expected response:
```json
{
  "status": "healthy",
  "video_processor": "ready",
  "ai_model": "Gemini 2.5 Flash Lite",
  "whisper_model": "OpenAI Whisper (base)",
  "database": "connected",
  "storage": "connected"
}
```

### Test Frontend
```bash
cd frontend
npm run build
npm run preview
```

Visit http://localhost:4173

---

## 7️⃣ Cost Breakdown

### Monthly Costs (1000 videos processed)

| Service | Free Tier | Paid (1000 videos) |
|---------|-----------|-------------------|
| **Neon DB** | 0.5GB | Free |
| **Cloudflare R2** | 10GB, 1M requests | $0.75 |
| **Railway** | $5 credit | $15 |
| **Vercel** | 100GB bandwidth | Free |
| **Gemini API** | 15 req/min | $60 |
| **Total** | **$0** | **~$75.75/month** |

### Cost Optimization Tips

1. **Use Free Tiers**
   - Neon: Free for small databases
   - R2: Free for first 10GB
   - Vercel: Free for most traffic

2. **Optimize Storage**
   - Delete old clips after 30 days
   - Compress videos before upload
   - Use lower resolution for previews

3. **Optimize AI Usage**
   - Cache transcriptions
   - Batch process videos
   - Use smaller Whisper model (tiny)

4. **Monitor Usage**
   - Set up billing alerts
   - Track API usage
   - Monitor storage growth

### Estimated Costs by Scale

| Videos/Month | Database | Storage | Backend | AI | Total |
|--------------|----------|---------|---------|-----|-------|
| 100 | Free | Free | Free | $6 | **$6** |
| 500 | Free | Free | $5 | $30 | **$35** |
| 1000 | Free | $1 | $15 | $60 | **$76** |
| 5000 | $19 | $5 | $50 | $300 | **$374** |
| 10000 | $19 | $10 | $100 | $600 | **$729** |

---

## 8️⃣ Security Checklist

### Before Going Live

- [ ] Generate strong SECRET_KEY
- [ ] Never commit .env files
- [ ] Enable HTTPS (Railway/Vercel do this automatically)
- [ ] Configure CORS for production domain only
- [ ] Set up rate limiting (already implemented)
- [ ] Enable database backups (Neon does this automatically)
- [ ] Set up error monitoring (Sentry recommended)
- [ ] Add logging and monitoring
- [ ] Test all endpoints
- [ ] Test file upload limits
- [ ] Test authentication flow

### Environment Variables Security

**Never expose:**
- SECRET_KEY
- GEMINI_API_KEY
- DATABASE_URL
- STORAGE credentials

**Use environment variables:**
- Railway: Project → Variables
- Vercel: Project Settings → Environment Variables
- Never hardcode in source code

---

## 9️⃣ Monitoring & Maintenance

### Set Up Monitoring

**1. Error Tracking (Sentry)**
```bash
pip install sentry-sdk
```

Add to `main.py`:
```python
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

**2. Uptime Monitoring**
- Use UptimeRobot (free)
- Monitor: https://your-app.railway.app/health
- Get alerts if down

**3. Cost Monitoring**
- Neon: Dashboard → Usage
- Cloudflare: R2 → Analytics
- Railway: Project → Usage
- Gemini: https://aistudio.google.com/app/apikey

### Regular Maintenance

**Weekly:**
- Check error logs
- Monitor API usage
- Review storage usage

**Monthly:**
- Review costs
- Clean up old files
- Update dependencies
- Check security updates

**Quarterly:**
- Database optimization
- Performance review
- Cost optimization
- Feature planning

---

## 🎯 Quick Start Checklist

- [ ] 1. Create Neon database → Get DATABASE_URL
- [ ] 2. Create Cloudflare R2 bucket → Get storage credentials
- [ ] 3. Update backend/.env with all variables
- [ ] 4. Test locally: `python main.py` → Check /health
- [ ] 5. Deploy backend to Railway
- [ ] 6. Update frontend API_URL
- [ ] 7. Deploy frontend to Vercel
- [ ] 8. Update CORS in backend
- [ ] 9. Test production: Register → Upload → Process → Download
- [ ] 10. Set up monitoring and alerts

---

## 🆘 Troubleshooting

### "Database connection failed"
- Check DATABASE_URL format
- Verify Neon project is active
- Check firewall/network settings
- Test connection with psql

### "Storage upload failed"
- Verify R2 credentials
- Check bucket permissions
- Verify endpoint URL
- Test with AWS CLI

### "CORS error in browser"
- Add frontend domain to CORS whitelist
- Redeploy backend
- Clear browser cache
- Check browser console for exact error

### "Video processing timeout"
- Check Railway logs
- Increase timeout limits
- Use smaller videos for testing
- Check Gemini API quota

### "Out of memory"
- Upgrade Railway plan
- Optimize video processing
- Use smaller Whisper model
- Process videos in chunks

---

## 📚 Additional Resources

- **Neon Docs**: https://neon.tech/docs
- **Cloudflare R2 Docs**: https://developers.cloudflare.com/r2/
- **Railway Docs**: https://docs.railway.app/
- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/

---

## ✅ You're Ready for Production!

Once all steps are complete:
1. Your database stores all user data persistently
2. Your clips are saved to cloud storage (no temp file issues!)
3. Your backend auto-scales with traffic
4. Your frontend is globally distributed
5. Total cost: $0-75/month depending on usage

**Next Steps:**
- Test with real users
- Monitor performance
- Optimize costs
- Add new features
- Scale as needed

Good luck! 🚀
