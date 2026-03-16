# Monte Carlo Simulations

A full-stack application for running Monte Carlo simulations of various games with configurable parameters.

## Project Overview

This application allows you to run statistical simulations and analyze outcomes for:
- **Blackjack**: Compare 8 different playing strategies
- **Poker**: Texas Hold'em with 8 player personality types
- **Snakes & Ladders**: Board game probability analysis
- **Tic-Tac-Toe**: Random play outcome distributions

## Architecture

### Backend (FastAPI + Python)
- RESTful API with automatic documentation
- Modular simulation engines
- Pydantic models for validation
- CORS-enabled for frontend integration

### Frontend (React + Vite)
- Modern React 19 with hooks
- React Router for navigation
- Axios for API communication
- CSS Modules for styling
- Responsive design

## Quick Start

### Prerequisites
- Python 3.8+ (for backend)
- Node.js 16+ (for frontend)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at:
- **Application**: http://localhost:5173

## Usage

1. Navigate to http://localhost:5173
2. Choose a simulation from the home page
3. Configure parameters in the sidebar
4. Click "Run Simulation"
5. View detailed results and statistics

## Features

### Blackjack
- **Strategies**: Never Bust, Safe, Basic, Aggressive, Mimic Dealer, Gut Feel, Card Counter, Martingale
- **Configurable**: Decks, payouts, rules (splits, double down, soft 17)
- **Metrics**: Win rate, ROI, net profit, blackjacks, busts

### Poker (Texas Hold'em)
- **Strategies**: Calling Station, Tight Passive/Aggressive, Loose Aggressive, Pot Odds, Bluffer, Position Aware, GTO
- **Configurable**: Blinds, starting stacks, rebuys
- **Metrics**: Win rate, VPIP, PFR, net profit, pot sizes

### Snakes & Ladders
- **Configurable**: Board size, number of snakes/ladders, bounce-back rule
- **Metrics**: Win rates, game length distribution, average rolls

### Tic-Tac-Toe
- **Configurable**: Board size (3x3, 4x4, 5x5)
- **Metrics**: Win/loss/draw rates, first-player advantage

## Project Structure

```
Monte-Carlo-Simulations/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── models/              # Pydantic schemas
│   ├── routers/             # API endpoints
│   └── simulations/         # Simulation engines
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── utils/           # Utilities (API client)
│   │   └── App.jsx          # Main app component
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation with:
- Request/response schemas
- Parameter descriptions
- Try-it-out functionality
- Example requests

## Technology Stack

**Backend:**
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)
- Python standard library (random, statistics)

**Frontend:**
- React 19 (UI framework)
- Vite 8 (build tool)
- React Router (routing)
- Axios (HTTP client)
- CSS Modules (styling)

## Development

### Adding a New Simulation

1. **Backend:**
   - Create simulation engine in `backend/simulations/`
   - Add Pydantic models in `backend/models/schemas.py`
   - Create router in `backend/routers/`
   - Register router in `backend/main.py`

2. **Frontend:**
   - Create page component in `frontend/src/pages/`
   - Add API methods in `frontend/src/utils/api.js`
   - Add route in `frontend/src/App.jsx`
   - Add navigation link in Navigation component

## Code Quality

- **Modular**: Separation of concerns with clear boundaries
- **Type-safe**: Pydantic validation on backend
- **Documented**: Inline comments and API docs
- **Styled**: Consistent design with CSS Modules
- **Responsive**: Mobile-friendly interface

## License

This project is for educational purposes.

## Contributing

Contributions are welcome! Please follow the existing code structure and styling conventions.
