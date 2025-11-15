# AI ATS Tracker - Quick Start & Usage Guide

## Quick Start (5 Minutes)

### Step 1: Install Dependencies

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Step 2: Configure Environment

Create a `.env` file in the backend directory:
```bash
OPENAI_API_KEY=your_actual_openai_api_key_here
```

Get your OpenAI API key from: https://platform.openai.com/api-keys

### Step 3: Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 4: Open Application

Open your browser and go to: http://localhost:3000

## Using the Application

### 1. Upload a Candidate

1. Click **"Upload Candidate"** in the navigation bar
2. **Drag & drop** or **click to select** a CV/Resume file
   - Supported formats: PDF, DOCX, TXT
3. (Optional) Upload a cover letter
4. Click **"Upload & Analyze Candidate"**
5. Wait for analysis to complete (30-60 seconds)

### 2. View Candidates Dashboard

- Click **"Dashboard"** in the navigation
- See all processed candidates with their scores
- Status indicators show processing state:
  - 🟢 **Completed** - Analysis finished
  - 🟡 **Processing** - Currently analyzing
  - 🔴 **Failed** - Error occurred
  - ⚪ **Pending** - Waiting to be analyzed

### 3. View Detailed Report

1. Click on any candidate in the dashboard
2. View comprehensive report including:
   - **Overall Score** (out of 100)
   - **CV Analysis** (60 points)
     - Work experience evaluation
     - Skills assessment
     - Education review
     - Career progression
     - Achievements
   - **Cover Letter Analysis** (40 points - if provided)
     - Writing quality
     - Motivation
     - Company fit
     - Communication skills
   - **Contact Validation**
     - Email verification
     - Phone format check
     - LinkedIn profile
   - **Background Check Guidance**
     - Online presence recommendations
     - Social media verification steps
     - Work experience verification guidance

### 4. Sample Data

Use the provided sample files in `sample_data/` for testing:
- `sample_cv.txt` - Example CV
- `sample_cover_letter.txt` - Example cover letter

## Understanding the Scores

### Overall Score (100 points)
- **80-100**: Excellent candidate, strong match
- **60-79**: Good candidate, worth interviewing
- **40-59**: Average candidate, consider carefully
- **0-39**: Weak candidate, may not be a good fit

### CV Score (60 points breakdown)
- Work Experience: 20 points
- Skills Match: 15 points
- Education: 10 points
- Career Progression: 8 points
- Achievements: 5 points
- Presentation: 2 points

### Cover Letter Score (40 points breakdown)
- Writing Quality: 12 points
- Motivation: 10 points
- Company Fit: 8 points
- Specific Examples: 7 points
- Communication: 3 points

## API Usage

### API Documentation
Once backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Example API Calls

**Upload Candidate:**
```bash
curl -X POST http://localhost:8000/api/candidates/upload \
  -F "cv_file=@path/to/cv.pdf" \
  -F "cover_letter_file=@path/to/cover_letter.pdf"
```

**Analyze Candidate:**
```bash
curl -X POST http://localhost:8000/api/candidates/1/analyze
```

**List Candidates:**
```bash
curl http://localhost:8000/api/candidates/
```

**Get Candidate Details:**
```bash
curl http://localhost:8000/api/candidates/1
```

**Delete Candidate:**
```bash
curl -X DELETE http://localhost:8000/api/candidates/1
```

## Tips & Best Practices

### For Best Results

1. **CV Quality**: Upload clear, well-formatted CVs
   - PDF or DOCX preferred over TXT
   - Ensure text is selectable (not scanned images)
   - Include complete contact information

2. **Cover Letter**: Always include cover letter when available
   - Significantly improves overall score
   - Provides insights into motivation and fit

3. **Information Extraction**: The system automatically extracts:
   - Name (usually first line of CV)
   - Email addresses
   - Phone numbers
   - LinkedIn URLs
   - Skills list

### Common Issues

**"Error analyzing candidate"**
- Check that OPENAI_API_KEY is set correctly
- Ensure you have OpenAI API credits
- Try with a smaller document

**"Invalid file format"**
- Only PDF, DOCX, and TXT are supported
- Ensure file isn't corrupted
- Try converting to a different format

**"Cannot connect to API"**
- Verify backend is running on port 8000
- Check CORS settings if accessing from different domain
- Ensure no firewall blocking

**"No candidates showing"**
- Click "Refresh" button
- Check backend console for errors
- Verify database file exists

## Advanced Features

### Custom Scoring Weights

Edit `backend/app/services/ai_analyzer.py` to adjust scoring weights:
```python
# Change these values in the prompts
work_experience_points = 20  # default
skills_points = 15  # default
# etc.
```

### Database Management

View database:
```bash
cd backend
sqlite3 ats_tracker.db
.tables
SELECT * FROM candidates;
.quit
```

Clear database:
```bash
rm backend/ats_tracker.db
# Restart backend to recreate
```

### Export Candidate Data

```bash
# Export as JSON
curl http://localhost:8000/api/candidates/1 > candidate_1.json

# Or use the API in your code
import requests
response = requests.get('http://localhost:8000/api/candidates/1')
candidate_data = response.json()
```

## Workflow Examples

### Example 1: Batch Processing
1. Upload multiple candidates one by one
2. Each gets analyzed automatically
3. View all candidates in dashboard
4. Sort mentally by score
5. Review top candidates in detail

### Example 2: Detailed Review
1. Upload candidate
2. Review overall score first
3. If score is high (>70), read detailed breakdown
4. Check strengths align with job requirements
5. Review background check recommendations
6. Make hiring decision

### Example 3: Comparison
1. Upload all applicants for a position
2. View dashboard to see all scores
3. Click through top 5 candidates
4. Compare CV analysis and cover letter quality
5. Note any red flags in background checks
6. Shortlist for interviews

## Performance

- **Upload Time**: 1-5 seconds
- **Analysis Time**: 30-60 seconds (depends on OpenAI API)
- **Concurrent Users**: Backend can handle multiple simultaneous analyses
- **File Size Limit**: Default 10MB (configurable)

## Cost Considerations

OpenAI API costs approximately:
- **$0.01-0.03 per candidate** (using GPT-3.5-turbo)
- **$0.10-0.30 per candidate** (using GPT-4)

100 candidates ≈ $1-3 (GPT-3.5) or $10-30 (GPT-4)

Monitor usage at: https://platform.openai.com/usage

## Security Notes

- API keys stored in environment variables (not in code)
- Candidate data stored locally in SQLite
- No data sent to third parties (except OpenAI for analysis)
- CORS configured to prevent unauthorized access
- Input validation on file uploads

## Getting Help

1. Check the troubleshooting section in README.md
2. Review API documentation at /docs
3. Check backend logs for error messages
4. Verify environment configuration
5. Open an issue on GitHub

## Next Steps

After getting comfortable with basic usage:
1. Integrate with your existing HR workflow
2. Customize scoring criteria for your needs
3. Add custom fields to candidate model
4. Export reports to PDF (future feature)
5. Set up automated email notifications

## Contributing

Want to improve the system?
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)

---

**Happy Recruiting! 🎯**

If this system helps you find great candidates, consider giving it a star on GitHub!
