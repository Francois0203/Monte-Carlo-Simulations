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
- RESTful API with automatic documentation (Swagger UI & ReDoc)
- Modular simulation engines
- Pydantic models for request/response validation
- CORS-enabled for frontend integration
- Structured router-based endpoints

### Frontend (React + Vite)
- Modern React 19 with hooks
- React Router for client-side routing
- Axios for HTTP communication
- CSS Modules for component-scoped styling
- Responsive design with mobile, tablet, and desktop breakpoints
- Error boundaries for graceful error handling

## Quick Start

### Prerequisites
- Python 3.8+ (for backend)
- Node.js 16+ (for frontend)

### Using Start Scripts
The easiest way to run the application:

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
./start.sh
```

### Manual Setup

#### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Application**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at:
- **Application**: http://localhost:5173

### Environment Variables
The frontend uses environment variables (already configured in `.env`):
```env
VITE_API_URL=http://localhost:8000
```

## Usage

1. Navigate to http://localhost:5173
2. Choose a simulation from the home page
3. Configure parameters in the sidebar
4. Click "Run Simulation"
5. View detailed results and statistics

## Features

### Blackjack
- **Strategies**: Never Bust, Safe, Basic, Aggressive, Mimic Dealer, Gut Feel, Card Counter, Martingale
- **Configurable**: Decks (1-8), blackjack payouts (1.5x or 2x), dealer stands on soft 17, splits, double down, ace high/low
- **Metrics**: Win rate, ROI, net profit, blackjacks, busts, push rate
- **API Endpoint**: `POST /api/blackjack/simulate`

### Poker (Texas Hold'em)
- **Strategies**: Calling Station, Tight Passive, Tight Aggressive, Loose Aggressive, Pot Odds Player, Bluffer, Position Aware, GTO Balanced
- **Configurable**: Blinds, starting stacks, rebuys, number of hands
- **Metrics**: Win rate, VPIP (Voluntarily Put in Pot), PFR (Pre-Flop Raise), net profit, average pot sizes
- **API Endpoint**: `POST /api/poker/simulate`

### Snakes & Ladders
- **Configurable**: Board size (20-100 squares), number of snakes (1-10), number of ladders (1-10), bounce-back rule
- **Metrics**: Win rates per player position, game length distribution, average rolls to completion
- **API Endpoint**: `POST /api/snakes-and-ladders/simulate`

### Tic-Tac-Toe (Naughts & Crosses)
- **Configurable**: Board size (3x3, 4x4, 5x5)
- **Metrics**: Win/loss/draw rates, first-player advantage analysis
- **API Endpoint**: `POST /api/naughts-and-crosses/simulate`

## API Examples

### Blackjack Simulation
```bash
curl -X POST "http://localhost:8000/api/blackjack/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "num_games": 10000,
    "num_decks": 6,
    "blackjack_payout": 1.5,
    "dealer_stands_soft": true,
    "allow_splits": true,
    "allow_double_down": true,
    "ace_high": true,
    "players": ["basic", "aggressive", "card_counter"]
  }'
```

### Poker Simulation
```bash
curl -X POST "http://localhost:8000/api/poker/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "num_hands": 1000,
    "num_players": 6,
    "small_blind": 5,
    "big_blind": 10,
    "starting_stack": 1000,
    "allow_rebuys": true,
    "strategies": ["tight_aggressive", "loose_aggressive", "gto_balanced"]
  }'
```

### Snakes and Ladders Simulation
```bash
curl -X POST "http://localhost:8000/api/snakes-and-ladders/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "num_games": 10000,
    "num_players": 2,
    "board_size": 34,
    "num_snakes": 5,
    "num_ladders": 5,
    "bounce_back": true
  }'
```

### Tic-Tac-Toe Simulation
```bash
curl -X POST "http://localhost:8000/api/naughts-and-crosses/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "num_games": 10000,
    "board_size": 3
  }'
```

## Project Structure

```
Monte-Carlo-Simulations/
├── backend/
│   ├── main.py                    # FastAPI application entry point
│   ├── requirements.txt           # Python dependencies
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py            # Pydantic request/response models
│   ├── routers/                   # API endpoint handlers
│   │   ├── __init__.py
│   │   ├── blackjack.py
│   │   ├── poker.py
│   │   ├── snakes_and_ladders.py
│   │   └── naughts_and_crosses.py
│   └── simulations/               # Simulation engines
│       ├── __init__.py
│       ├── blackjack_sim.py
│       ├── poker_sim.py
│       ├── snakes_and_ladders_sim.py
│       └── naughts_and_crosses_sim.py
├── frontend/
│   ├── public/                    # Static assets
│   ├── src/
│   │   ├── components/            # Reusable UI components
│   │   │   ├── ChartCard/
│   │   │   ├── ErrorBoundary/     # Error handling component
│   │   │   ├── ErrorMessage/      # Error display component
│   │   │   ├── LoadingSpinner/    # Loading indicator
│   │   │   ├── NavigationBar/     # Main navigation
│   │   │   ├── StatCard/
│   │   │   └── ThemeSwitch/       # Dark/light theme toggle
│   │   ├── hooks/                 # Custom React hooks
│   │   │   └── useTheme.js
│   │   ├── pages/                 # Page components
│   │   │   ├── Home/              # Landing page
│   │   │   ├── Blackjack/         # Blackjack simulation page
│   │   │   ├── Poker/             # Poker simulation page
│   │   │   ├── SnakesAndLadders/  # Snakes & Ladders page
│   │   │   └── NaughtsAndCrosses/ # Tic-Tac-Toe page
│   │   ├── styles/                # Global styles
│   │   │   ├── Theme.css          # Theme variables
│   │   │   ├── Components.css     # Component base styles
│   │   │   └── Wrappers.css       # Layout wrappers
│   │   ├── utils/
│   │   │   └── api.js             # Axios API client
│   │   ├── App.jsx                # Main app with routing
│   │   └── main.jsx               # Application entry point
│   ├── package.json
│   ├── vite.config.js
│   └── eslint.config.js
├── start.bat                       # Windows startup script
├── start.sh                        # Linux/Mac startup script
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
- FastAPI (modern web framework)
- Uvicorn (ASGI server)
- Pydantic (data validation & serialization)
- Python standard library (random, statistics)

**Frontend:**
- React 19 (UI framework with hooks)
- Vite 8 (fast build tool and dev server)
- React Router (client-side routing)
- Axios (HTTP client for API requests)
- CSS Modules (component-scoped styling)

## Available Scripts

### Backend
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
- `npm run dev` - Start development server on port 5173
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint code quality checks

## Development

### Adding a New Simulation

1. **Backend:**
   - Create simulation engine in `backend/simulations/<name>_sim.py`
   - Define game logic, strategies, and statistics calculation
   - Add Pydantic request/response models in `backend/models/schemas.py`
   - Create router endpoint in `backend/routers/<name>.py`
   - Register router in `backend/main.py` with `app.include_router()`

2. **Frontend:**
   - Create page component in `frontend/src/pages/<Name>/`
   - Build configuration form and results display
   - Add API methods in `frontend/src/utils/api.js`
   - Add route in `frontend/src/App.jsx` within React Router
   - Add navigation link in `NavigationBar` component

### Component Structure
Each simulation page follows a consistent pattern:
1. Configuration form in a sticky sidebar
2. Results display in the main content area
3. Loading states with spinner
4. Error handling with ErrorMessage component
5. Responsive design with CSS modules
6. Statistics cards and charts for visualization

### Styling Guidelines
- Use CSS Modules for component-scoped styles
- Leverage CSS custom properties (variables) from `Theme.css`
- Follow responsive design patterns (mobile-first)
- Maintain consistent spacing with `--spacing-*` variables
- Use semantic color variables (`--accent-1`, `--error-color`, etc.)

## Code Quality

- **Modular**: Clear separation of concerns with dedicated modules
- **Type-safe**: Pydantic validation ensures data integrity
- **Documented**: Inline comments and comprehensive API documentation
- **Styled**: Consistent design system with CSS Modules
- **Responsive**: Mobile, tablet, and desktop optimized
- **Error-handled**: Graceful error boundaries and user feedback

## License

This project is for educational purposes.

## Contributing

Contributions are welcome! Please follow these guidelines:
- Follow existing code structure and styling conventions
- Use descriptive variable names and add comments for complex logic
- Test your changes locally before submitting
- Ensure API endpoints include proper validation and documentation
- Maintain responsive design in frontend components
- Update this README if adding new features or changing setup instructions

## Support

For issues, questions, or suggestions:
- Check the API documentation at http://localhost:8000/docs
- Review error messages in browser console (F12)
- Ensure both backend and frontend servers are running
- Verify Python and Node.js versions meet requirements
