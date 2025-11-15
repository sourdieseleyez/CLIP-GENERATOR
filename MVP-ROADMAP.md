# ClipGen Marketplace MVP Roadmap

## 🎯 Vision
A two-sided marketplace where celebrities/brands post campaigns and clippers create viral clips for tiered revenue share.

## ✅ What's Built (v2.0)

### Core Features
- ✅ AI-powered clip generation (Gemini + Whisper)
- ✅ User authentication & profiles
- ✅ Dashboard with analytics
- ✅ Clips library
- ✅ Cloud storage (S3-compatible)
- ✅ Job queue system (Redis/RQ)

### Marketplace Features (NEW)
- ✅ Campaign posting (clients)
- ✅ Campaign browsing (clippers)
- ✅ Job claiming system
- ✅ Tiered revenue splits (Bronze/Silver/Gold/Platinum)
- ✅ Job submission & review flow
- ✅ Payout request system
- ✅ User tier progression

### Database Schema
```
users - Extended with marketplace fields (role, tier, earnings, rating)
campaigns - Client job postings
marketplace_jobs - Links campaigns to clippers
payouts - Payment tracking
clips - Enhanced with performance tracking
```

## 🚀 MVP Launch Checklist (Week 1)

### Day 1-2: Core Setup
- [ ] Set up production database (Neon/Railway)
- [ ] Configure environment variables
- [ ] Test marketplace API endpoints
- [ ] Deploy backend to Railway/Render

### Day 3-4: Frontend Polish
- [ ] Add campaign creation form for clients
- [ ] Test marketplace flow end-to-end
- [ ] Add loading states and error handling
- [ ] Mobile responsive testing

### Day 5: YouTube Integration
- [ ] YouTube OAuth setup
- [ ] Auto-upload with tracking links
- [ ] View count polling (daily cron)
- [ ] Revenue calculation

### Day 6: Payment Setup
- [ ] Manual payout process documentation
- [ ] Payout approval dashboard (admin)
- [ ] Email notifications for payouts

### Day 7: Launch Prep
- [ ] Beta testing with 5 users
- [ ] Bug fixes
- [ ] Landing page
- [ ] Launch! 🎉

## 📊 Revenue Model (Tiered)

### Clipper Tiers
| Tier | Split | Requirements |
|------|-------|--------------|
| Bronze | 70/30 | New users (default) |
| Silver | 75/25 | 10+ approved clips OR 100k+ views |
| Gold | 80/20 | 50+ approved clips OR 500k+ views |
| Platinum | 85/15 | 100+ approved clips OR 1M+ views |

### Platform Revenue Streams
1. **Revenue Share** - 15-30% per clip (based on tier)
2. **Marketplace Fee** - 5-10% on campaign budgets (future)
3. **Subscriptions** - Client tiers (future)
4. **Premium Tools** - AI upsells for clippers (future)

## 🎯 Post-MVP Features (v2.1+)

### Week 2-3: Payments
- [ ] Stripe Connect integration
- [ ] Automatic payouts
- [ ] Payment history
- [ ] Tax forms (1099)

### Week 4: Analytics
- [ ] Deep performance insights
- [ ] A/B testing for clips
- [ ] Virality predictions
- [ ] Competitor analysis

### Month 2: Growth
- [ ] Referral system
- [ ] Leaderboards
- [ ] Clipper portfolios
- [ ] Client subscriptions
- [ ] White-label for agencies

### Month 3: Scale
- [ ] Multi-platform support (TikTok, Instagram)
- [ ] Bulk campaign posting
- [ ] Team accounts
- [ ] API for integrations

## 💰 Pricing Strategy

### For Clients (Pay-per-Campaign)
- **Starter**: $50-100 per clip
- **Pro**: $100-250 per clip (priority, faster turnaround)
- **Enterprise**: Custom pricing (dedicated clippers, SLA)

### For Clippers (Free to Join)
- No upfront costs
- Earn based on tier
- Withdraw anytime (min $50)

## 📈 Success Metrics

### Month 1 Goals
- 20 active clippers
- 5 paying clients
- 100 clips generated
- $5,000 GMV (Gross Marketplace Value)

### Month 3 Goals
- 100 active clippers
- 25 paying clients
- 1,000 clips generated
- $50,000 GMV

### Month 6 Goals
- 500 active clippers
- 100 paying clients
- 10,000 clips generated
- $250,000 GMV

## 🛠 Tech Stack

### Backend
- FastAPI (Python)
- PostgreSQL (Neon)
- Redis (Upstash)
- S3 (Cloudflare R2)
- Gemini 2.5 Flash Lite
- Whisper (STT)

### Frontend
- React + Vite
- Lucide Icons
- CSS Variables

### Infrastructure
- Railway/Render (API)
- Vercel/Netlify (Frontend)
- GitHub Actions (CI/CD)

## 🎨 Brand Positioning

**Tagline**: "Turn any video into viral clips. Get paid."

**Value Props**:
- For Clippers: "Earn money creating viral clips with AI"
- For Clients: "Get professional clips 10x faster, 5x cheaper"

**Differentiators**:
1. AI-powered (133x cheaper than GPT-4)
2. Tiered rewards (earn more as you improve)
3. Full-service (we handle YouTube uploads & tracking)
4. Fair splits (up to 85/15)

## 📞 Next Steps

1. **Test the marketplace flow**
   ```bash
   # Start backend
   cd backend
   python main.py
   
   # Start frontend
   cd frontend
   npm run dev
   ```

2. **Create test campaign**
   - Login as client
   - Post a campaign
   - Switch to clipper account
   - Claim and complete job

3. **Deploy to production**
   - Set up Railway project
   - Configure environment variables
   - Deploy and test

4. **Launch beta**
   - Invite 10 beta users
   - Collect feedback
   - Iterate quickly

---

**Ready to ship?** Let's finalize the MVP and get this to market! 🚀
