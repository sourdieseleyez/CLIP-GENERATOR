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

## Gemini video processor (required by default)

This backend uses the Gemini AI model (via `GeminiVideoProcessor`) as the primary video editing/clip-generation engine.

- Set `GEMINI_API_KEY` in your `.env` (copy from `.env.example`).
- By default the app treats Gemini as required. If `REQUIRE_GEMINI=true` and `GEMINI_API_KEY` is not set, the service will fail to start.
- For local development you can set `REQUIRE_GEMINI=false` to allow the service to run without Gemini, but `/videos/process` will return 503 if the processor is unavailable when the flag is true.

Example `.env` entries:

```ini
GEMINI_API_KEY=AIzaSyBoq3hadikVYF4rlpZ6G9Jv2KYe_0FKu7Y
REQUIRE_GEMINI=true
```

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
