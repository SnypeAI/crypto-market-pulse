# Crypto Market Pulse Web Interface

This is the web interface for the Crypto Market Pulse project. It provides real-time cryptocurrency market analysis, price predictions, and technical indicators.

## Features

- Real-time market data
- Price predictions with confidence scores
- Technical analysis indicators
- Model performance monitoring
- Alert system

## Development

### Prerequisites

- Node.js >= 16
- Python >= 3.10

### Setup

1. Install dependencies:
   ```bash
   pip install -e .
   ```

2. Start development server:
   ```bash
   uvicorn src.api.main:app --reload
   ```

3. Open web interface:
   - Visit `http://localhost:8000`

## Deployment

The site is automatically deployed to GitHub Pages when changes are pushed to the main branch.

## License

MIT License