# AI ATS Tracker - Deployment Guide

This guide covers various deployment options for the AI ATS Tracker application.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Considerations](#production-considerations)

## Local Development

### Prerequisites
- Python 3.8+
- Node.js 18+
- Google Gemini API key

### Setup Steps

1. **Clone Repository**
```bash
git clone https://github.com/fmuoria/ai-ats-tracker.git
cd ai-ats-tracker
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd ../frontend
npm install
```

4. **Environment Configuration**
```bash
# Create .env in backend directory
echo "GEMINI_API_KEY=your_key_here" > backend/.env
```

5. **Run Application**
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

6. **Access Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Docker Deployment

### Create Dockerfiles

**Backend Dockerfile** (`backend/Dockerfile`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile** (`frontend/Dockerfile`):
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production image
FROM node:18-alpine

WORKDIR /app

# Copy built application
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "start"]
```

**Docker Compose** (`docker-compose.yml`):
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DATABASE_URL=sqlite:///./ats_tracker.db
      - CORS_ORIGINS=http://localhost:3000,http://frontend:3000
    volumes:
      - ./backend/ats_tracker.db:/app/ats_tracker.db
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - API_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped
```

### Deploy with Docker Compose

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Cloud Deployment

### Option 1: Vercel (Frontend) + Railway (Backend)

#### Deploy Backend to Railway

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Login and Deploy**
```bash
cd backend
railway login
railway init
railway add
```

3. **Set Environment Variables**
```bash
railway variables set GEMINI_API_KEY=your_key_here
railway variables set DATABASE_URL=sqlite:///./ats_tracker.db
```

4. **Deploy**
```bash
railway up
```

#### Deploy Frontend to Vercel

1. **Install Vercel CLI**
```bash
npm install -g vercel
```

2. **Configure**
```bash
cd frontend
# Update .env.production
echo "API_URL=https://your-backend.railway.app" > .env.production
```

3. **Deploy**
```bash
vercel
```

### Option 2: AWS Elastic Beanstalk

#### Backend Deployment

1. **Install EB CLI**
```bash
pip install awsebcli
```

2. **Initialize**
```bash
cd backend
eb init -p python-3.11 ai-ats-tracker-backend
```

3. **Create Environment**
```bash
eb create production
```

4. **Set Environment Variables**
```bash
eb setenv GEMINI_API_KEY=your_key_here
```

5. **Deploy**
```bash
eb deploy
```

#### Frontend Deployment

Use AWS Amplify:
1. Connect GitHub repository
2. Configure build settings
3. Set environment variables
4. Deploy

### Option 3: Google Cloud Platform

#### Backend on Cloud Run

1. **Build Container**
```bash
cd backend
gcloud builds submit --tag gcr.io/PROJECT_ID/ats-backend
```

2. **Deploy**
```bash
gcloud run deploy ats-backend \
  --image gcr.io/PROJECT_ID/ats-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key_here
```

#### Frontend on Firebase Hosting

1. **Build**
```bash
cd frontend
npm run build
```

2. **Deploy**
```bash
firebase init hosting
firebase deploy
```

### Option 4: Heroku

#### Backend

1. **Create Heroku App**
```bash
cd backend
heroku create ats-tracker-backend
```

2. **Set Environment Variables**
```bash
heroku config:set GEMINI_API_KEY=your_key_here
```

3. **Create Procfile**
```bash
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile
```

4. **Deploy**
```bash
git push heroku main
```

#### Frontend

1. **Create Heroku App**
```bash
cd frontend
heroku create ats-tracker-frontend
```

2. **Add Node.js Buildpack**
```bash
heroku buildpacks:set heroku/nodejs
```

3. **Deploy**
```bash
git push heroku main
```

## Production Considerations

### 1. Database

**Migrate from SQLite to PostgreSQL:**

```python
# backend/.env
DATABASE_URL=postgresql://user:password@host:5432/atsdb
```

**Install PostgreSQL adapter:**
```bash
pip install psycopg2-binary
```

### 2. Environment Variables

**Required for Production:**
```env
GEMINI_API_KEY=your_key
DATABASE_URL=postgresql://...
SECRET_KEY=random_secret_key
CORS_ORIGINS=https://yourdomain.com
DEBUG=False
```

### 3. Security

**Backend Security Checklist:**
- [ ] Set DEBUG=False
- [ ] Use HTTPS only
- [ ] Configure proper CORS origins
- [ ] Set strong SECRET_KEY
- [ ] Enable rate limiting
- [ ] Use secure database connection
- [ ] Validate all inputs
- [ ] Keep dependencies updated

**Frontend Security Checklist:**
- [ ] Enable HTTPS
- [ ] Set proper CSP headers
- [ ] Sanitize user inputs
- [ ] Use environment variables for API URLs
- [ ] Enable security headers

### 4. Performance Optimization

**Backend:**
```python
# Use production WSGI server
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

**Frontend:**
```bash
# Build for production
npm run build
npm start
```

**Database:**
- Add indexes on frequently queried fields
- Use connection pooling
- Implement caching (Redis)

### 5. Monitoring

**Backend Monitoring:**
```python
# Add logging
import logging
logging.basicConfig(level=logging.INFO)

# Add health check monitoring
# Use services like:
# - Datadog
# - New Relic
# - Sentry (error tracking)
```

**Frontend Monitoring:**
- Use Vercel Analytics
- Google Analytics
- Error tracking (Sentry)

### 6. Backup Strategy

**Database Backups:**
```bash
# PostgreSQL
pg_dump atsdb > backup_$(date +%Y%m%d).sql

# Automated backups
0 2 * * * pg_dump atsdb > /backups/atsdb_$(date +\%Y\%m\%d).sql
```

**File Backups:**
```bash
# Backup uploaded files
tar -czf uploads_backup.tar.gz uploads/
```

### 7. Scaling

**Horizontal Scaling:**
- Deploy multiple backend instances
- Use load balancer
- Implement session storage (Redis)
- Use CDN for static assets

**Vertical Scaling:**
- Increase server resources
- Optimize database queries
- Implement caching

### 8. SSL/TLS Certificate

**Let's Encrypt (Free):**
```bash
# Using Certbot
sudo certbot --nginx -d yourdomain.com
```

**Cloud Provider:**
- Most cloud providers offer free SSL certificates
- AWS Certificate Manager
- Google Cloud Load Balancer
- Cloudflare

### 9. Domain Configuration

**DNS Settings:**
```
Type    Name    Value
A       @       your.server.ip
CNAME   www     yourdomain.com
A       api     backend.server.ip
```

### 10. Cost Estimation

**Google Gemini API:**
- Gemini 1.5 Flash: FREE (up to 60 requests/minute)
- Free tier with generous daily limits
- No cost for typical ATS usage

**Infrastructure (Monthly):**
- Small (< 100 candidates/month): $5-15
- Medium (< 1000 candidates/month): $15-30
- Large (> 1000 candidates/month): $50+

**Breakdown:**
- Backend hosting: $5-50
- Frontend hosting: $0-20 (Vercel free tier)
- Database: $0-30 (depends on size)
- Gemini API: FREE

## Deployment Checklist

### Pre-Deployment
- [ ] Test all features locally
- [ ] Run backend tests
- [ ] Check environment variables
- [ ] Update dependencies
- [ ] Review security settings
- [ ] Backup existing data

### Deployment
- [ ] Deploy database (if separate)
- [ ] Deploy backend
- [ ] Deploy frontend
- [ ] Configure DNS
- [ ] Set up SSL certificate
- [ ] Test all endpoints
- [ ] Verify API connectivity

### Post-Deployment
- [ ] Monitor error logs
- [ ] Test with sample data
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Document deployment
- [ ] Share URLs with team

## Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check logs
docker logs backend
# or
journalctl -u ats-backend

# Verify environment variables
env | grep GEMINI_API_KEY
```

**Database connection error:**
```bash
# Check DATABASE_URL format
# PostgreSQL: postgresql://user:pass@host:5432/db
# MySQL: mysql://user:pass@host:3306/db

# Test connection
psql $DATABASE_URL
```

**Frontend can't connect to backend:**
```bash
# Verify API_URL in frontend
echo $API_URL

# Check CORS settings in backend
# Ensure frontend URL is in CORS_ORIGINS
```

**Gemini API errors:**
```bash
# Verify API key is set
echo $GEMINI_API_KEY

# Get API key from: https://aistudio.google.com/app/apikey
# Check usage and quotas in Google AI Studio
```

## Maintenance

### Regular Updates

**Monthly:**
- Update dependencies
- Review logs
- Check API usage
- Backup database

**Quarterly:**
- Security audit
- Performance review
- Cost optimization
- Feature planning

### Support

For deployment issues:
1. Check logs first
2. Review documentation
3. Search existing issues
4. Create new issue with details

## Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Docker Documentation](https://docs.docker.com/)
- [AWS Documentation](https://docs.aws.amazon.com/)
- [Vercel Documentation](https://vercel.com/docs)

---

**Need Help?** Open an issue on GitHub with deployment questions.
