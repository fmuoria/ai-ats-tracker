# AI-Powered ATS Tracker

A comprehensive Applicant Tracking System (ATS) that leverages AI to provide intelligent candidate evaluation through document analysis, online presence verification, and background checks.

## Features

### 🎯 Core Capabilities
- **Document Processing**: Upload and parse CVs and cover letters (PDF, DOCX, TXT)
- **Job Description Matching**: Upload job descriptions and match candidates semantically
- **AI-Powered Scoring**: Intelligent evaluation of candidates out of 100%
  - CV Analysis (60% weight)
  - Cover Letter Analysis (40% weight)
  - Job Description Match Score (semantic similarity)
  - Final Combined Score (structural + semantic fit)
- **Skill Matching**: Automatic identification of matched and missing skills
- **Background Checks**: Online presence and social media verification
- **Enhanced Social Search**: Automated web search via SerpAPI or manual guidance
- **Modern Web Interface**: Clean, responsive dashboard for managing candidates

### 📊 Scoring System
The system provides comprehensive analysis including:
- **Structural CV Analysis (60 points)**
  - Work experience evaluation
  - Skills assessment
  - Education qualifications review
  - Career progression analysis
  - Professional achievements
  - Document quality and presentation
- **Cover Letter Analysis (40 points)**
  - Writing quality and communication skills
  - Motivation and company fit assessment
- **Job Description Matching (NEW)**
  - Semantic similarity score (0-100%)
  - Matched skills identification
  - Missing skills analysis
  - Final combined score: CV structural (60%) + JD semantic match (40%)

### 🔍 Background Verification
- Contact information validation (email, phone)
- LinkedIn profile verification
- **Enhanced Online Presence Search**
  - Automated web search via SerpAPI (when API key configured)
  - Manual search guidance (fallback)
  - Multiple platform checking (LinkedIn, GitHub, Twitter, etc.)
- Social media presence analysis
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
- Google Gemini API key (replaces OpenAI)
- SerpAPI key (optional, for automated web searches)

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
- `GEMINI_API_KEY`: Your Google Gemini API key for AI-powered analysis (get it from https://makersuite.google.com/app/apikey)

**Optional Environment Variables:**
- `SERPAPI_KEY` or `SEARCH_API_KEY`: For automated web/social media searches (get it from https://serpapi.com/)
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

### 1. Upload Candidate Documents

1. Click the "Upload Candidate" button in the navigation
2. Drag and drop or select a CV/Resume file (required)
3. Optionally, upload a cover letter
4. Click "Upload & Analyze Candidate"

### 2. View Candidates Dashboard

- Navigate to the "Dashboard" tab
- See all processed candidates with their scores
- Click on any candidate to view detailed analysis

### 3. Candidate Report

The detailed report includes:
- Overall score out of 100
- CV and cover letter score breakdown
- Strengths and areas for improvement
- Contact information validation
- Online presence assessment
- Social media verification guidance
- Work experience verification recommendations

### 4. Background Checks

The system provides guidance for:
- Email validation (professional vs personal domain)
- Phone number format validation
- LinkedIn profile verification
- Manual verification recommendations for social media
- Company website checks for employment verification

## API Endpoints

### Job Descriptions (NEW)

- `POST /api/job-descriptions/` - Create job description (file or text)
- `GET /api/job-descriptions/` - List all job descriptions
- `GET /api/job-descriptions/{id}` - Get job description details
- `DELETE /api/job-descriptions/{id}` - Delete job description

### Candidates

- `POST /api/candidates/upload` - Upload CV and cover letter
- `POST /api/candidates/{id}/analyze?jd_id={jd_id}` - Analyze candidate (optionally with job description)
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
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Google Gemini API**: AI-powered document analysis
- **Sentence Transformers**: Local semantic embeddings for job matching
- **PyPDF2 & python-docx**: Document parsing
- **SerpAPI**: Automated web and social media search (optional)
- **BeautifulSoup4**: Web scraping capabilities

### Frontend
- **Next.js 14**: React framework
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client
- **react-dropzone**: File upload component

## Features in Detail

### Document Parser
Extracts key information from CVs and cover letters:
- Candidate name
- Email address
- Phone number
- LinkedIn URL
- Skills list

### AI Analyzer
Uses OpenAI GPT models to:
- Evaluate CV content with detailed scoring
- Analyze cover letter quality
- Provide constructive feedback
- Generate overall assessment

### Background Checker
Performs validation and provides guidance for:
- Email format and professionalism check
- Phone number format validation
- LinkedIn profile verification
- Online presence search recommendations
- Social media verification guidance
- Work experience verification recommendations

## Security Considerations

- API keys stored in environment variables
- File upload validation (type and size)
- Input sanitization
- CORS configuration
- Secure database connections

## Limitations and Notes

1. **Web Scraping**: Automated web scraping and social media checks require additional API access and are provided as manual verification guidance to respect platform terms of service.

2. **LinkedIn**: Direct LinkedIn scraping violates their ToS. The system validates URL format and provides guidance for manual verification.

3. **Employment Verification**: Automated employment verification requires specialized services. The system provides guidance for manual verification through company websites and LinkedIn.

4. **API Costs**: The OpenAI API usage incurs costs based on token usage. Monitor your usage in the OpenAI dashboard.

## Troubleshooting

### Backend Issues

**Error: "GEMINI_API_KEY environment variable is not set"**
- Ensure you've created a `.env` file in the backend directory
- Add your Gemini API key: `GEMINI_API_KEY=your_key_here`
- Get your key from https://makersuite.google.com/app/apikey

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

Completed:
- [x] Job description upload and matching
- [x] Semantic similarity scoring with sentence-transformers
- [x] Combined structural + semantic scoring
- [x] Automated social/online presence search
- [x] Enhanced skill matching (matched vs missing)

Future enhancements:
- [ ] PDF report export functionality
- [ ] Batch processing of multiple candidates
- [ ] Advanced search and filtering
- [ ] Custom scoring criteria configuration
- [ ] Email notifications
- [ ] Integration with job posting platforms
- [ ] Advanced analytics and reporting
- [ ] Real-time collaboration features
- [ ] Background job queue (Celery/Redis) for large-scale processing

## Acknowledgments

- Google for Gemini API
- Sentence Transformers team for semantic embeddings
- SerpAPI for web search capabilities
- FastAPI and Next.js communities
- All open-source contributors