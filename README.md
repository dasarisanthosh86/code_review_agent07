# AI Code Review Agent

Automated code analysis, issue detection, and intelligent fixes powered by AI.

## Features
- 🔍 Smart code analysis
- 🛠️ Automatic code fixes
- 📊 Detailed change reports
- 🚀 GitHub integration

## Setup

### Backend
```bash
cd backend_full
pip install -r requirements.txt
python -m app.main
```

### Frontend
```bash
cd frontend_full
npm install
npm run dev
```

## Usage
1. Enter GitHub repository URL
2. Enter your GitHub token (required for pushing fixes)
3. Upload scan report (JSON)
4. Get automated fixes and updated repository

## GitHub Token
You must provide your GitHub token via the UI form when submitting a review. The token is required to push automated fixes to your repository.

**Note**: Your token is only used for the current request and is not stored.
