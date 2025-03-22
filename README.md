# Autonomous Legal Document Analyzer

An AI-powered legal document analysis system that autonomously reads, interprets, and summarizes legal documents, extracts key clauses, detects risks, and generates comprehensive reports.

## Features

- 📄 Document Upload & Processing
- 🔍 Intelligent Clause Detection
- ⚠️ Risk Analysis
- 📝 Automated Summarization
- 🔐 Privacy-First Approach
- 🤖 AI-Powered Analysis
- 📊 Interactive Dashboard

## Tech Stack

- **Frontend**: React, Tailwind CSS
- **Backend**: FastAPI, Python
- **Database**: MongoDB
- **AI/ML**: 
  - PyTorch/TensorFlow
  - Hugging Face Transformers
  - SpaCy
  - OpenAI/LLaMA Integration
  - Stable Baselines3 (RL)
- **Deployment**: Docker, AWS/GCP

## Project Structure

```
.
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core functionality
│   │   ├── models/         # Database models
│   │   └── services/       # Business logic
│   ├── ml/
│   │   ├── models/         # ML model definitions
│   │   ├── training/       # Training scripts
│   │   └── utils/          # ML utilities
│   └── tests/              # Backend tests
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── utils/         # Utility functions
│   └── public/            # Static assets
├── docker/                # Docker configuration
│   ├── backend/
│   └── frontend/
└── docs/                  # Documentation
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/legal-document-analyzer.git
   cd legal-document-analyzer
   ```

2. Backend Setup:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Frontend Setup:
   ```bash
   cd frontend
   npm install
   ```

4. Environment Configuration:
   - Copy `.env.example` to `.env` in both frontend and backend directories
   - Configure necessary API keys and database connections

5. Start Development Servers:
   ```bash
   # Backend
   cd backend
   uvicorn app.main:app --reload

   # Frontend
   cd frontend
   npm run dev
   ```

## Development Guidelines

- Follow PEP 8 style guide for Python code
- Use ESLint and Prettier for JavaScript/TypeScript code
- Write unit tests for new features
- Document API endpoints using OpenAPI/Swagger
- Follow Git flow for branch management

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
