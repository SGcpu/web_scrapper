# Review Radar MVP

A comprehensive review analysis platform that combines web scraping, ML-powered sentiment analysis, and browser extension capabilities to provide actionable insights from product reviews across e-commerce platforms.

## 🌟 Features

- **URL-Based Web Scraper**: Robust module that extracts customer reviews from major e-commerce sites
- **Pre-trained Sentiment Analysis**: Uses Hugging Face models for accurate sentiment classification
- **Keyword & Topic Extraction**: Advanced NLP techniques for identifying key product attributes
- **Interactive Dashboard**: Clean, user-friendly interface with sentiment visualization
- **Chrome Extension**: Seamless browser integration for instant analysis
- **Aspect-Based Analysis**: Detailed breakdown of sentiment by product features

## 🏗️ Project Structure

```
review-radar/
├── backend/          # FastAPI + ML pipeline
├── frontend/         # React + Vite dashboard
├── extension/        # Chrome extension
├── shared/          # Shared types and utilities
├── docs/            # Documentation
├── venv/            # Python virtual environment
└── requirements.txt # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Webscraper_sentimental
```

2. Set up Python virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install chromium
```

5. Set up frontend:
```bash
cd frontend
npm install
```

## 📖 Development

### Backend Development
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Start FastAPI server
cd backend
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Extension Development
Load the extension directory in Chrome's developer mode.

## 🧪 Testing

```bash
# Backend tests
pytest backend/tests/

# Frontend tests
cd frontend
npm test
```

## 📝 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🛠️ Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Playwright, Transformers
- **Frontend**: React, TypeScript, Vite, Recharts
- **Extension**: Manifest V3, Content Scripts
- **ML**: Hugging Face Transformers, KeyBERT, BERTopic
- **Database**: SQLite

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For support and questions, please open an issue in the GitHub repository.