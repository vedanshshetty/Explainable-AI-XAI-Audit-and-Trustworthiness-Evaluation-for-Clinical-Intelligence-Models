# Clinical Intelligence System - Setup Guide

## Prerequisites
- Python 3.10+
- pip, git
- 8GB+ RAM (for model loading)

## Installation

```bash
# 1. Clone repository
git clone <repo-url>
cd clinical-intelligence-system

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

## Data Setup

```bash
# Download and build indexes
python scripts/setup.py
```

## Running the Backend

```bash
# Start the FastAPI backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Running the Frontend

```bash
# Start the Streamlit frontend
streamlit run frontend/app.py
```

## Running Tests

```bash
# Run unit tests
pytest tests/test_clinical_system.py -v

# Run verification gates
python scripts/verify.py --all
```
