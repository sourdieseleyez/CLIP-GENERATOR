# Development Mode Guide

## Quick Start for Testing

Development mode makes it easy to test the analytics and clips library features without going through the full registration/login flow.

### Features

1. **Dev Login Button** - One-click login with pre-configured dev account
2. **Seed Sample Data** - Generate 10 realistic sample clips with analytics
3. **Dev Mode Banner** - Visual indicator that you're in development mode
4. **No Rate Limits** - Test freely without restrictions

### How to Use

#### 1. Start the Application

```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

#### 2. Click "Dev Login"

When you open the app (http://localhost:5173), you'll see:
- A purple "Development Mode" banner at the top
- A "Dev Login" button in the sidebar (purple/blue color)

Click "Dev Login" and you'll be instantly logged in as `dev@clipgen.local`

#### 3. Seed Sample Data

After logging in, click the "Seed Sample Data" button in the sidebar to create:
- 10 sample clips with realistic data
- Views ranging from 28K to 156K
- Revenue from $0.76 to $12.48
- Mixed platforms (TikTok, YouTube, Instagram)
- Various categories (humor, educational, controversial, etc.)

#### 4. Explore the Features

Now you can:
- **Dashboard** - See analytics with real-looking data
- **Clips Library** - Browse, search, filter, and edit clips
- **Generate Clips** - Test the clip generation flow

### Sample Data Details

The seeded clips include:

| Hook | Platform | Views | Revenue | Category |
|------|----------|-------|---------|----------|
| "This is the craziest thing..." | TikTok | 125K | $3.75 | Surprising |
| "Here's why everyone is talking..." | YouTube | 85K | $6.80 | Controversial |
| "Wait for it... 😂" | Instagram | 67K | $1.34 | Humor |
| "This will blow your mind" | YouTube | 45K | $3.60 | Educational |
| "The moment that changed everything" | TikTok | 92K | $2.76 | Emotional |
| ...and 5 more clips |

### Dev Mode Indicators

When in development mode, you'll see:
- 🌟 Purple "Development Mode" banner at top
- 🌟 Purple "Dev Login" button (when logged out)
- 🌟 Purple "Seed Sample Data" button (when logged in)

### Disabling Dev Mode

To disable dev mode for production:

**Backend (.env):**
```bash
ENVIRONMENT=production
```

**Frontend:**
Dev mode is automatically disabled in production builds (`npm run build`)

### Dev Endpoints

These endpoints are only available when `ENVIRONMENT=development`:

**POST /dev/login**
- Creates/returns dev user
- No credentials needed
- Returns JWT token

**POST /dev/seed-data**
- Creates 10 sample clips
- Requires authentication
- Realistic analytics data

### Security Notes

⚠️ **Important:**
- Dev mode is automatically disabled in production builds
- Dev endpoints check `ENVIRONMENT` variable
- Never deploy with `ENVIRONMENT=development`
- Dev login uses a fixed password (not secure for production)

### Troubleshooting

**"Dev login failed"**
- Make sure backend is running
- Check that `ENVIRONMENT=development` in .env
- Verify backend logs for errors

**"Failed to seed data"**
- Database must be configured (PostgreSQL)
- Make sure you're logged in first
- Check backend logs for database errors

**Dev buttons not showing**
- Frontend must be running in dev mode (`npm run dev`)
- Check browser console for errors
- Try refreshing the page

### Testing Workflow

Recommended testing flow:

1. **First Time Setup**
   ```bash
   # Click "Dev Login"
   # Click "Seed Sample Data"
   # Go to Dashboard
   ```

2. **Test Analytics**
   - View dashboard stats
   - Check platform breakdown
   - See top performing clips

3. **Test Clips Library**
   - Search for clips
   - Filter by platform/category
   - Sort by different metrics
   - Edit a clip's analytics
   - Download a clip

4. **Test Clip Generation**
   - Go to "Generate Clips"
   - Upload a video or use YouTube URL
   - Process and generate clips
   - See new clips in library

### Resetting Data

To reset and start fresh:

**Option 1: Clear Database**
```bash
# If using PostgreSQL
# Drop and recreate tables (backend will auto-create on restart)
```

**Option 2: Use Different Dev Account**
```python
# In backend/main.py, change dev_email
dev_email = "dev2@clipgen.local"
```

**Option 3: Delete Specific Clips**
```bash
# Use Clips Library UI to manage clips
# Or use database tools to delete records
```

### Development Tips

1. **Fast Iteration**
   - Keep both terminals running
   - Frontend hot-reloads automatically
   - Backend restarts on code changes (if using --reload)

2. **Testing Analytics**
   - Seed data multiple times to test with more clips
   - Edit clip analytics to test different scenarios
   - Try different filter/sort combinations

3. **Testing UI**
   - Resize browser to test responsive design
   - Test with different data volumes
   - Check loading states

4. **Debugging**
   - Check browser console for frontend errors
   - Check backend terminal for API errors
   - Use browser DevTools Network tab for API calls

### Production Checklist

Before deploying to production:

- [ ] Set `ENVIRONMENT=production` in .env
- [ ] Change `SECRET_KEY` to secure random value
- [ ] Configure real database (PostgreSQL)
- [ ] Configure cloud storage (S3/R2)
- [ ] Remove or secure dev endpoints
- [ ] Test with real authentication
- [ ] Verify dev buttons don't appear

---

Happy testing! 🚀
