# Clip Generator Backend

FastAPI backend for the Clip Generator application.

## Setup

1. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env and set your SECRET_KEY
   ```

## Running the Backend

Start the FastAPI server:

```bash
cd backend
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /users/register` - Register a new user
- `POST /token` - Login and get access token

### Videos
- `POST /videos/upload` - Upload a video (requires authentication)
- `GET /videos` - Get user's uploaded videos (requires authentication)

## Notes

- This is a development setup with in-memory storage
- For production, replace the in-memory database with PostgreSQL/MongoDB
- Change the SECRET_KEY in production
- Add proper file storage (S3, etc.) for video files
