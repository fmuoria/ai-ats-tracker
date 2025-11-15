# AI ATS Tracker - System Architecture

## Overview

The AI ATS Tracker is a full-stack web application that uses artificial intelligence to evaluate job candidates through document analysis and background verification.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                            │
│                      (http://localhost:3000)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/HTTPS
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      Frontend (Next.js)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Upload UI  │  │   Dashboard  │  │   Details    │          │
│  │  Component   │  │   Component  │  │   Component  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              API Service (Axios)                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ REST API Calls
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     Backend (FastAPI)                            │
│                    (http://localhost:8000)                       │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    API Endpoints                         │    │
│  │  • POST /api/candidates/upload                          │    │
│  │  • POST /api/candidates/{id}/analyze                    │    │
│  │  • GET  /api/candidates/                                │    │
│  │  • GET  /api/candidates/{id}                            │    │
│  │  • DELETE /api/candidates/{id}                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                             │                                     │
│  ┌──────────────────────────┼────────────────────────────────┐  │
│  │                      Services                             │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │   Document   │  │      AI      │  │  Background  │   │  │
│  │  │    Parser    │  │   Analyzer   │  │   Checker    │   │  │
│  │  │              │  │              │  │              │   │  │
│  │  │ PDF/DOCX/TXT │  │ OpenAI GPT   │  │ Validation & │   │  │
│  │  │  Extraction  │  │  Analysis    │  │    Guidance  │   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                     │
│  ┌──────────────────────────▼────────────────────────────────┐  │
│  │                    Database (SQLite)                      │  │
│  │              Candidates, Scores, Analysis                 │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ API Calls
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      OpenAI API                                  │
│                  GPT-3.5-turbo / GPT-4                           │
│              (AI-Powered Document Analysis)                      │
└──────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Layer

**Technology**: Next.js 14 + React + TypeScript + Tailwind CSS

**Components**:
- **FileUpload**: Handles drag-and-drop file uploads
- **CandidateList**: Displays all candidates with scores
- **CandidateDetails**: Shows detailed analysis reports
- **API Service**: Axios-based HTTP client

**Key Features**:
- Responsive design
- Real-time status updates
- Type-safe code with TypeScript
- Modern UI with Tailwind CSS

### Backend Layer

**Technology**: Python FastAPI + SQLAlchemy + OpenAI SDK

**API Endpoints**:
1. `POST /api/candidates/upload` - Upload documents
2. `POST /api/candidates/{id}/analyze` - Trigger analysis
3. `GET /api/candidates/` - List all candidates
4. `GET /api/candidates/{id}` - Get candidate details
5. `DELETE /api/candidates/{id}` - Remove candidate

**Services**:

1. **Document Parser**
   - Extracts text from PDF, DOCX, TXT
   - Parses candidate information
   - Regex-based entity extraction
   - Skills identification

2. **AI Analyzer**
   - OpenAI GPT integration
   - CV scoring (60 points)
   - Cover letter scoring (40 points)
   - Detailed feedback generation

3. **Background Checker**
   - Email validation
   - Phone format checking
   - LinkedIn URL verification
   - Online presence guidance
   - Social media verification recommendations

### Data Layer

**Database**: SQLite (default) / PostgreSQL (production)

**Candidate Model**:
```python
- id (Primary Key)
- name, email, phone, linkedin_url
- cv_filename, cv_text
- cover_letter_filename, cover_letter_text
- overall_score, cv_score, cover_letter_score
- cv_analysis, cover_letter_analysis (JSON)
- work_experience, education, skills (JSON)
- online_presence, social_media_presence (JSON)
- work_verification (JSON)
- processing_status
- created_at, updated_at
```

## Data Flow

### 1. Upload & Parse Flow

```
User → Upload Files → Frontend
                        ↓
                   API Call (multipart/form-data)
                        ↓
                   Backend Endpoint
                        ↓
                   Document Parser
                        ↓
               Extract Text & Info
                        ↓
                 Save to Database
                        ↓
              Return Candidate ID
```

### 2. Analysis Flow

```
User → Click Analyze → Frontend
                         ↓
                    API Call
                         ↓
                  Backend Endpoint
                         ↓
            ┌────────────┴────────────┐
            ↓                         ↓
       AI Analyzer              Background Checker
            │                         │
     OpenAI API Call          Validation Logic
            │                         │
    CV + Cover Letter           Contact Check
      Scoring                  Online Presence
            │                         │
    Detailed Feedback            Guidance
            │                         │
            └────────────┬────────────┘
                         ↓
                 Save Results to DB
                         ↓
                 Update Status
                         ↓
               Return Analysis
```

### 3. View Flow

```
User → View Dashboard → Frontend
                          ↓
                     API Call
                          ↓
                   Backend Endpoint
                          ↓
               Query Database
                          ↓
            Return Candidate List
                          ↓
              Frontend Display
```

## Scoring Algorithm

### Overall Score Calculation

```
IF cover_letter_provided:
    overall_score = cv_score + cover_letter_score
    (Max: 60 + 40 = 100 points)
ELSE:
    overall_score = (cv_score / 60) * 100
    (Normalized to 100 points)
```

### CV Scoring (60 points)

```
Work Experience      20 points
Skills Match         15 points
Education           10 points
Career Progression   8 points
Achievements         5 points
Presentation         2 points
─────────────────────────────
Total               60 points
```

### Cover Letter Scoring (40 points)

```
Writing Quality     12 points
Motivation          10 points
Company Fit          8 points
Examples             7 points
Communication        3 points
─────────────────────────────
Total               40 points
```

## AI Integration

### OpenAI API Usage

**Model**: GPT-3.5-turbo (cost-effective) or GPT-4 (higher quality)

**Process**:
1. Prepare document text (first 4000 chars for CV, 3000 for cover letter)
2. Craft detailed prompt with scoring criteria
3. Request structured JSON response
4. Parse and validate response
5. Store results in database

**Prompt Engineering**:
- System role: Expert HR recruiter
- Structured output format (JSON)
- Clear scoring criteria
- Request for specific feedback categories

**Error Handling**:
- Fallback scores on API failure
- Retry logic for transient errors
- Graceful degradation

## Security Measures

### API Security
- Environment variables for secrets
- CORS configuration
- Input validation
- File type validation
- Size limits on uploads

### Data Security
- Encrypted database connections (production)
- No sensitive data in logs
- Secure file handling
- API key protection

### Privacy
- Data stored locally
- No third-party sharing (except OpenAI for analysis)
- GDPR considerations
- User data control

## Scalability Considerations

### Current Design
- Async/await for I/O operations
- Database connection pooling
- Stateless backend (horizontal scaling ready)
- Frontend static generation capable

### Future Scaling
- Add Redis for caching
- Implement job queue (Celery) for long-running tasks
- Migrate to PostgreSQL for better concurrency
- Add CDN for static assets
- Implement load balancing
- Use cloud storage for documents

## Deployment Architecture

### Development
```
Local Machine
├── Backend: localhost:8000
└── Frontend: localhost:3000
```

### Production (Example)
```
                     [Load Balancer]
                           │
          ┌────────────────┼────────────────┐
          ↓                                 ↓
    [Frontend Server]              [Backend Server(s)]
    (Vercel/Netlify)              (Docker/Cloud Run)
          │                                 │
          │                        [Database Server]
          │                        (PostgreSQL/RDS)
          │                                 │
          └─────────────────────────────────┘
```

## Performance Metrics

### Target Performance
- **Page Load**: < 2 seconds
- **Upload Time**: < 5 seconds
- **Analysis Time**: 30-60 seconds (dependent on OpenAI API)
- **API Response**: < 200ms (excluding analysis)

### Optimization Techniques
- Code splitting (Next.js automatic)
- Image optimization
- Database indexing on frequently queried fields
- API response caching (future)
- Lazy loading of components

## Monitoring & Logging

### Backend Logging
- Request/response logging
- Error tracking
- Performance metrics
- OpenAI API usage tracking

### Frontend Logging
- Error boundary for React errors
- Console errors in development
- User action tracking (optional)

### Health Checks
- `/health` endpoint
- Database connectivity check
- External API availability

## Technology Choices Rationale

### Why FastAPI?
- Modern Python async framework
- Automatic API documentation
- Type hints and validation
- High performance
- Easy testing

### Why Next.js?
- Server-side rendering capability
- Built-in routing
- API routes option
- Optimized production builds
- Great developer experience

### Why SQLite (default)?
- Zero configuration
- File-based (easy backup)
- Sufficient for small-medium scale
- Easy migration to PostgreSQL

### Why OpenAI?
- State-of-the-art language understanding
- Flexible prompt engineering
- JSON response format
- Cost-effective (GPT-3.5)
- Scalable

## Extension Points

### Easy to Add
- Additional document formats
- Custom scoring criteria
- More background check sources
- Email notifications
- PDF report generation
- User authentication
- Multi-tenant support
- Job posting management

### Integration Ready
- Calendar systems (for scheduling interviews)
- Email services (SendGrid, Mailgun)
- Cloud storage (S3, GCS)
- HR systems (BambooHR, Workday)
- Video interview platforms

## Maintenance

### Regular Tasks
- Update dependencies
- Monitor OpenAI API usage
- Backup database
- Review logs for errors
- Update AI prompts for better accuracy

### Upgrades
- Python packages: `pip install --upgrade`
- Node packages: `npm update`
- Database schema: Alembic migrations
- Model improvements: Update prompts

## Conclusion

The AI ATS Tracker is designed as a modular, scalable, and maintainable system that leverages modern web technologies and AI to streamline candidate evaluation. The architecture supports easy extension and modification while maintaining security and performance standards.
