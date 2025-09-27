# Review Radar - Web Scraping & Sentiment Analysis Tool

A comprehensive review analysis platform that scrapes e-commerce product reviews and provides sentiment analysis to deliver actionable insights through an interactive dashboard.

## 🌟 Current Implementation Status

### Completed Features:
- **Robust Web Scraper**: 
  - Amazon product scraper with anti-bot measures
  - Fallback mechanisms for handling authentication challenges
  - Detailed debugging and logging capabilities

- **Backend API Infrastructure**: 
  - FastAPI endpoints for product and review management
  - Background task processing for scraping operations
  - Database models for products, reviews, and scraping sessions

- **Frontend Dashboard**: 
  - Basic UI for product review visualization
  - Displays scraped reviews and analysis results
  - Real-time scraping status updates

### In Progress:
- **Sentiment Analysis Integration**: Connecting pre-trained sentiment models
- **Enhanced Error Handling**: Improved resilience in scraping operations
- **Support for Additional E-commerce Sites**: Beyond Amazon

## 🏗️ Project Structure

```
Webscraper_sentimental/
├── backend/                   # FastAPI backend application
│   ├── app/                   # Core application
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core configurations
│   │   ├── database/          # Database connections
│   │   ├── models/            # Data models
│   │   └── scrapers/          # Web scrapers for different sites
│   ├── debug_screenshots/     # Debug screenshots from scraper runs
│   └── main.py                # FastAPI application entry point
├── frontend/                  # React/TypeScript frontend
│   ├── public/                # Static assets
│   └── src/                   # Source code
│       ├── components/        # React components
│       ├── hooks/             # Custom React hooks
│       └── services/          # API services
├── docs/                      # Project documentation
└── venv/                      # Python virtual environment
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
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Quick Setup
Run the `setup.ps1` PowerShell script to automatically set up the entire project:
```powershell
.\setup.ps1
```

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

- **Backend**: FastAPI, SQLAlchemy, Playwright for browser automation
- **Frontend**: React, TypeScript, Vite
- **Database**: SQLite
- **Web Scraping**: Custom scrapers with anti-detection mechanisms
- **Future ML Integration**: Hugging Face Transformers for sentiment analysis

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