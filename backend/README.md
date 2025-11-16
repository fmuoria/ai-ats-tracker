# AI ATS Tracker - Backend

FastAPI-based backend for the AI-Powered Applicant Tracking System.

## Features

- RESTful API with FastAPI
- SQLite database with SQLAlchemy ORM
- Google Gemini integration for AI-powered analysis
- Document parsing (PDF, DOCX, TXT)
- Background checking capabilities
- Automatic API documentation

## Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the backend directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./ats_tracker.db
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000
```

## Running

### Development

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── candidates.py      # Candidate endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py        # Database setup
│   │   └── candidate.py       # Candidate model
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_parser.py # Document parsing
│   │   ├── ai_analyzer.py     # AI analysis
│   │   └── background_checker.py # Background checks
│   ├── utils/
│   ├── __init__.py
│   └── main.py                # FastAPI application
└── requirements.txt
```

## API Endpoints

### Candidates

#### Upload Documents
```
POST /api/candidates/upload
Content-Type: multipart/form-data

Form Data:
- cv_file: file (required)
- cover_letter_file: file (optional)

Response:
{
  "message": "Candidate documents uploaded successfully",
  "candidate_id": 1,
  "status": "pending_analysis"
}
```

#### Analyze Candidate
```
POST /api/candidates/{candidate_id}/analyze

Response:
{
  "message": "Analysis completed successfully",
  "candidate_id": 1,
  "overall_score": 85.5,
  "status": "completed"
}
```

#### List Candidates
```
GET /api/candidates/

Response:
{
  "total": 10,
  "candidates": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "overall_score": 85.5,
      "processing_status": "completed",
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

#### Get Candidate Details
```
GET /api/candidates/{candidate_id}

Response:
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "overall_score": 85.5,
  "cv_score": 52.0,
  "cover_letter_score": 33.5,
  "cv_analysis": {...},
  "cover_letter_analysis": {...},
  "online_presence": {...},
  "social_media_presence": {...},
  "work_verification": {...}
}
```

#### Delete Candidate
```
DELETE /api/candidates/{candidate_id}

Response:
{
  "message": "Candidate deleted successfully"
}
```

## Services

### Document Parser

Handles parsing of different document formats:
- PDF parsing using PyPDF2
- DOCX parsing using python-docx
- TXT parsing
- Information extraction (email, phone, LinkedIn, skills)

### AI Analyzer

Uses Google Gemini AI for:
- CV content analysis and scoring
- Cover letter evaluation
- Detailed feedback generation
- Overall assessment calculation

### Background Checker

Provides validation and verification guidance:
- Email format validation
- Phone number validation
- LinkedIn profile verification
- Online presence search guidance
- Social media verification recommendations
- Work experience verification guidance

## Database

The application uses SQLite by default with SQLAlchemy ORM.

### Candidate Model

Fields:
- Basic info: name, email, phone, linkedin_url
- Documents: cv_filename, cv_text, cover_letter_filename, cover_letter_text
- Scores: overall_score, cv_score, cover_letter_score
- Analysis results: cv_analysis, cover_letter_analysis
- Background: online_presence, social_media_presence, work_verification
- Metadata: created_at, updated_at, processing_status

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Development

### Adding New Endpoints

1. Create endpoint function in `app/api/`
2. Add to router
3. Include router in `main.py`

### Adding New Services

1. Create service class in `app/services/`
2. Import in `app/services/__init__.py`
3. Use in API endpoints

## Security

- API keys in environment variables
- File upload validation
- Input sanitization
- CORS configuration
- Database connection security

## Error Handling

The API returns standard HTTP status codes:
- 200: Success
- 400: Bad Request (invalid input)
- 404: Not Found
- 500: Internal Server Error

Error responses include descriptive messages:
```json
{
  "detail": "Error message here"
}
```

## Performance Considerations

- Async endpoints for I/O operations
- Database connection pooling
- File upload size limits
- Rate limiting (optional)

## Monitoring

- Health check endpoint: `/health`
- Logging configured for debugging
- Database query logging (development only)
