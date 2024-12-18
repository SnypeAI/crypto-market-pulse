# Development Setup Guide

## Prerequisites

- Node.js >= 16
- Python >= 3.8
- SQLite3

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SnypeAI/crypto-market-pulse.git
cd crypto-market-pulse
```

2. Install dependencies:
```bash
npm install
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Initialize the database:
```bash
python scripts/init_db.py
```

5. Start development server:
```bash
npm run dev
```

## Development Workflow

1. Create feature branch
2. Make changes
3. Run tests
4. Submit PR

## Testing

```bash
npm test
python -m pytest
```

## Deployment

1. Build the project
2. Update environment variables
3. Run database migrations
4. Deploy