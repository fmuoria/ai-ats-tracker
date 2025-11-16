# AI-Powered ATS Tracker

A comprehensive Applicant Tracking System (ATS) that leverages AI to provide intelligent candidate evaluation through document analysis, online presence verification, and background checks.

## Features

### 🎯 Core Capabilities
- **Document Processing**: Upload and parse CVs and cover letters (PDF, DOCX, TXT)
- **Job Description Management**: Create and manage job postings for candidate matching
- **AI-Powered Scoring**: Intelligent evaluation of candidates with Google Gemini
  - Resume analysis with job description matching
  - Local embedding-based similarity scoring
  - Skills gap analysis
- **Smart Matching**: Semantic matching between resumes and job descriptions
  - 60% weight: Job description match score
  - 40% weight: CV quality score
- **Background Checks**: Online presence and social media verification with SerpAPI (optional)
- **Modern Web Interface**: Clean, responsive dashboard for managing jobs and candidates

### 📊 Scoring System
The system provides comprehensive analysis including:
- **Job Description Matching** (using local embeddings)
  - Semantic similarity between resume and job description
  - Skills matching analysis
  - Identification of matched and missing skills
- **Resume Quality Assessment** (using Google Gemini)
  - Work experience evaluation
  - Skills assessment
  - Education qualifications review
  - Career progression analysis
  - Professional achievements
- **Final Score Calculation**
  - With JD: 60% × JD Match Score + 40% × CV Quality Score
  - Without JD: CV Quality Score normalized to 100

### 🔍 Background Verification
- Contact information validation (email, phone)
- LinkedIn profile verification
- Online presence search using SerpAPI (optional)
- Social media presence analysis
- Automatic fallback to manual verification when API unavailable
- Work experience verification guidance

## Project Structure

```
ai-ats-tracker/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   │   ├── document_parser.py
│   │   │   ├── ai_analyzer.py
│   │   │   └── background_checker.py
│   │   └── main.py      # FastAPI application
│   └── requirements.txt
├── frontend/            # Next.js React frontend
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── pages/      # Next.js pages
│   │   ├── services/   # API client
│   │   └── styles/     # CSS styles
│   └── package.json
├── .env.example         # Environment variables template
└── README.md
```

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn
- Google Gemini API key (required)
- SerpAPI key (optional, for social media search)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/fmuoria/ai-ats-tracker.git
cd ai-ats-tracker
```

### 2. Backend Setup

```bash
cd backend

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

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
# or
yarn install
```

### 4. Environment Configuration

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SERPAPI_KEY=your_serpapi_key_here  # Optional
```

**Required Environment Variables:**
- `GEMINI_API_KEY`: Your Google Gemini API key for AI-powered analysis

**Optional Environment Variables:**
- `EMBEDDING_MODEL`: Embedding model name (defaults to 'all-MiniLM-L6-v2')
- `SERPAPI_KEY`: SerpAPI key for social media profile search
- `SOCIAL_SEARCH_ENABLED`: Enable/disable social search (defaults to 'true')
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `CORS_ORIGINS`: Allowed CORS origins (defaults to localhost:3000)

## Running the Application

### Start the Backend

```bash
cd backend

# Make sure virtual environment is activated
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Run the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Start the Frontend

In a new terminal:

```bash
cd frontend

# Run development server
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:3000`

## Usage Guide

### 1. Create Job Descriptions

1. Click the "Jobs" button in the navigation
2. Click "Create New" tab
3. Enter job title and paste the full job description
4. Click "Create Job Description"
5. The system will automatically generate embeddings for matching

### 2. Upload Candidate Documents

1. Click the "Upload Candidate" button in the navigation
2. Drag and drop or select a CV/Resume file (required)
3. Optionally, upload a cover letter
4. **Optional**: Select a job description for matching:
   - Choose from existing jobs in the dropdown, OR
   - Paste an ad-hoc job description for one-time matching
5. Click "Upload & Analyze Candidate"
6. Analysis runs in the background (check processing status)

### 3. View Candidates Dashboard

- Navigate to the "Dashboard" tab
- See all processed candidates with their scores
- Processing status indicators:
  - `pending_analysis`: Waiting to start
  - `analyzing`: AI analysis in progress
  - `completed`: Analysis finished
  - `error`: Processing failed
- Click on any candidate to view detailed analysis

### 4. Candidate Report

The detailed report includes:
- **Final Score** out of 100 (weighted combination)
- **JD Match Score**: Semantic similarity with job description
- **CV Quality Score**: AI assessment of resume quality
- **Skills Analysis**:
  - Matched skills (green badges)
  - Missing skills (orange badges)
- **AI Insights**:
  - Strengths
  - Gaps/Areas for improvement
  - Recommended interview questions
- **Social Media Presence**:
  - Platforms found (if SerpAPI enabled)
  - Topics of interest
  - Profile links
  - Manual check suggestions (if API unavailable)
- Contact information validation
- Background verification guidance

### 5. Job Description Matching

The system uses two complementary approaches:
1. **Semantic Matching**: Local embeddings (sentence-transformers) compute similarity between resume and JD
2. **AI Analysis**: Google Gemini identifies specific matched/missing skills and provides detailed insights

This dual approach ensures both quantitative matching scores and qualitative insights.

## API Endpoints

### Jobs

- `POST /api/jobs/` - Create new job description (generates embeddings)
- `GET /api/jobs/` - List all job descriptions
- `GET /api/jobs/{id}` - Get specific job description
- `DELETE /api/jobs/{id}` - Delete job description

### Candidates

- `POST /api/candidates/upload` - Upload CV and optional cover letter
  - Optional: `job_id` (integer) - Match against existing job
  - Optional: `job_text` (string) - Match against ad-hoc job description
  - Analysis runs automatically in background
- `POST /api/candidates/{id}/match` - Trigger job matching for existing candidate
  - Requires: `job_id` or `job_text`
- `POST /api/candidates/{id}/analyze` - Legacy: Analyze candidate documents
- `GET /api/candidates/` - List all candidates
- `GET /api/candidates/{id}` - Get candidate details
- `DELETE /api/candidates/{id}` - Delete candidate

### Health Check

- `GET /` - API root
- `GET /health` - Health check

## Development

### Backend Development

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Building for Production

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run build
npm start
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework with async support
- **SQLAlchemy**: SQL toolkit and ORM
- **Google Gemini API**: Advanced AI-powered document analysis
- **sentence-transformers**: Local embeddings for semantic matching
- **SerpAPI**: Optional social media profile search
- **PyPDF2 & python-docx**: Document parsing
- **BeautifulSoup4**: Web content extraction
- **NumPy**: Numerical operations for embeddings
- **FAISS**: Optional vector similarity search acceleration

### Frontend
- **Next.js 14**: React framework with SSR
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client
- **react-dropzone**: File upload component
- **lucide-react**: Modern icon library

## Features in Detail

### Document Parser
Extracts key information from CVs and cover letters:
- Candidate name
- Email address
- Phone number
- LinkedIn URL
- Skills list

### Embedding Service
Uses sentence-transformers for local semantic matching:
- Generates normalized embeddings for resumes and job descriptions
- Supports text chunking for long documents
- Computes cosine similarity for matching
- No external API calls - runs locally
- Model: all-MiniLM-L6-v2 (384-dimensional embeddings)

### AI Service (Gemini)
Uses Google Gemini API to:
- Analyze resume quality and content
- Match candidate skills against job requirements
- Identify matched and missing skills
- Provide strengths and improvement areas
- Generate recommended interview questions
- Calculate model fit score (0-100)

### Social Search Service
Optional SerpAPI integration for profile discovery:
- Searches public professional profiles (LinkedIn, GitHub, etc.)
- Extracts topics and expertise areas
- Provides profile links for verification
- Automatic fallback to manual verification
- Respects robots.txt and platform ToS
- No authenticated scraping

### Background Checker
Performs validation and provides guidance for:
- Email format and professionalism check
- Phone number format validation
- LinkedIn profile verification
- Online presence search recommendations
- Work experience verification recommendations

## Security Considerations

- API keys stored in environment variables
- File upload validation (type and size)
- Input sanitization
- CORS configuration
- Secure database connections

## Limitations and Notes

1. **Embedding Model**: The first run will download the sentence-transformers model (~90MB). Subsequent runs use the cached model.

2. **Social Media Search**: 
   - SerpAPI is optional and requires a paid API key
   - Without SerpAPI, the system provides manual verification guidance
   - Respects platform ToS - no authenticated scraping
   - LinkedIn profile scraping violates their ToS - use for URL validation only

3. **Background Processing**: 
   - Analysis runs asynchronously using FastAPI BackgroundTasks
   - Check `processing_status` field for progress
   - May take 30-60 seconds depending on document size and API response times

4. **API Costs**: 
   - Google Gemini API usage incurs costs based on token usage
   - SerpAPI charges per search query
   - Local embeddings run free on your hardware
   - Monitor usage in respective API dashboards

5. **Database Migrations**:
   - Simple migration helper included for MVP
   - For production, consider using Alembic for proper schema versioning

## Troubleshooting

### Backend Issues

**Error: "OPENAI_API_KEY environment variable is not set"**
- Ensure you've created a `.env` file in the backend directory
- Add your OpenAI API key: `OPENAI_API_KEY=your_key_here`

**Error: "Module not found"**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

### Frontend Issues

**Error: "Cannot connect to API"**
- Ensure backend is running on port 8000
- Check `API_URL` in frontend environment

**Error: "Module not found"**
- Run `npm install` in the frontend directory

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

## Roadmap

Future enhancements:
- [ ] PDF report export functionality
- [ ] Batch processing of multiple candidates
- [ ] Advanced search and filtering
- [ ] Custom scoring criteria configuration
- [ ] Email notifications
- [ ] Integration with job posting platforms
- [ ] Advanced analytics and reporting
- [ ] Real-time collaboration features

## Acknowledgments

- OpenAI for GPT API
- FastAPI and Next.js communities
- All open-source contributors