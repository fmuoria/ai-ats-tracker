# AI ATS Tracker - Frontend

Next.js-based frontend for the AI-Powered Applicant Tracking System.

## Features

- Modern React application with Next.js 14
- TypeScript for type safety
- Tailwind CSS for styling
- Responsive design
- File upload with drag-and-drop
- Real-time candidate dashboard
- Detailed candidate reports

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install
# or
yarn install
```

### Environment Configuration

Create a `.env.local` file (optional):

```env
API_URL=http://localhost:8000
```

By default, the frontend connects to `http://localhost:8000`.

## Running

### Development

```bash
npm run dev
# or
yarn dev
```

The application will be available at http://localhost:3000

### Production

```bash
# Build
npm run build
# or
yarn build

# Start
npm start
# or
yarn start
```

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # React components
│   │   ├── FileUpload.tsx
│   │   ├── CandidateList.tsx
│   │   └── CandidateDetails.tsx
│   ├── pages/          # Next.js pages
│   │   ├── _app.tsx
│   │   ├── _document.tsx
│   │   └── index.tsx
│   ├── services/       # API client
│   │   └── api.ts
│   ├── styles/         # Global styles
│   │   └── globals.css
│   └── utils/          # Utility functions
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## Components

### FileUpload

Drag-and-drop file upload component for CVs and cover letters.

Props:
- `onUpload(cvFile, coverLetterFile)`: Callback when files are uploaded
- `isUploading`: Loading state

Features:
- Accepts PDF, DOCX, TXT files
- Drag-and-drop support
- File preview with remove option
- Validation and error handling

### CandidateList

Displays list of all candidates with basic information.

Props:
- `candidates`: Array of candidate objects
- `onSelectCandidate(candidate)`: Callback when candidate is clicked

Features:
- Card-based layout
- Status badges
- Score display
- Click to view details

### CandidateDetails

Detailed view of a single candidate with full analysis.

Props:
- `candidate`: Candidate object with full details
- `onBack()`: Callback to return to list

Sections:
- Overall score display
- Candidate summary
- CV analysis breakdown
- Cover letter analysis
- Online presence information
- Social media verification
- Work experience verification

## API Service

The `api.ts` service provides methods for interacting with the backend:

```typescript
import { candidatesApi } from '@/services/api';

// Upload documents
const result = await candidatesApi.uploadDocuments(cvFile, coverLetterFile);

// Analyze candidate
await candidatesApi.analyzeCandidate(candidateId);

// List candidates
const data = await candidatesApi.listCandidates();

// Get candidate details
const candidate = await candidatesApi.getCandidateDetails(candidateId);

// Delete candidate
await candidatesApi.deleteCandidate(candidateId);
```

## Styling

The application uses Tailwind CSS for styling with a custom configuration:

- Primary color: Blue (#3b82f6)
- Responsive breakpoints
- Custom utility classes
- Component-specific styles

## Pages

### Home (/)

Main application page with three views:
1. **Dashboard**: List of all candidates
2. **Upload**: File upload interface
3. **Details**: Detailed candidate report

Navigation tabs switch between views.

## User Flow

1. User lands on dashboard (empty initially)
2. Clicks "Upload Candidate"
3. Uploads CV (and optionally cover letter)
4. System processes and analyzes documents
5. Returns to dashboard with new candidate
6. Clicks candidate to view detailed report
7. Reviews scores, analysis, and recommendations

## State Management

Uses React hooks for state management:
- `useState` for component state
- `useEffect` for data fetching
- Props for component communication

## Error Handling

- API errors displayed in alert messages
- Loading states during async operations
- Validation for file uploads
- User-friendly error messages

## Performance

- Code splitting with Next.js
- Image optimization
- CSS purging with Tailwind
- Lazy loading of components
- Efficient re-rendering

## Accessibility

- Semantic HTML
- ARIA labels
- Keyboard navigation
- Focus management
- Color contrast compliance

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development

### Adding New Components

```bash
# Create component
touch src/components/MyComponent.tsx

# Import in page
import MyComponent from '@/components/MyComponent';
```

### Styling Guidelines

- Use Tailwind utility classes
- Follow existing color scheme
- Maintain responsive design
- Use consistent spacing

### API Integration

```typescript
// Add new API method in services/api.ts
export const candidatesApi = {
  // existing methods...
  newMethod: async () => {
    const response = await api.get('/endpoint');
    return response.data;
  }
};
```

## Testing

```bash
# Add testing library
npm install --save-dev @testing-library/react @testing-library/jest-dom

# Run tests
npm test
```

## Building for Production

```bash
# Build
npm run build

# The output will be in the .next directory
# Deploy .next directory to your hosting service
```

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Other Platforms

Build the application and deploy the `.next` directory:
- Netlify
- AWS Amplify
- Digital Ocean
- Heroku

## Environment Variables

For production, set:
- `API_URL`: Backend API URL
- `NEXT_PUBLIC_API_URL`: Public-facing API URL (if different)

## Troubleshooting

### Cannot connect to API

Check:
1. Backend is running
2. CORS is configured correctly
3. API_URL is correct
4. Network/firewall settings

### Build errors

```bash
# Clear cache
rm -rf .next node_modules
npm install
npm run build
```

### Styling issues

```bash
# Rebuild Tailwind
npm run dev
# Refresh browser
```

## Contributing

1. Follow existing code style
2. Write descriptive commit messages
3. Test before submitting PR
4. Update documentation as needed
