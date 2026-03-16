# Monte Carlo Simulations Backend

FastAPI backend for running Monte Carlo simulations of various games.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Available Simulations

### Blackjack
- Endpoint: `/api/blackjack/simulate`
- Configurable parameters: num_games, num_decks, payouts, rules, player strategies
- Strategies: never_bust, safe, basic, aggressive, mimic_dealer, gut_feel, card_counter, martingale

### Poker
- Endpoint: `/api/poker/simulate`
- Configurable parameters: num_hands, num_players, blinds, stack size, rebuys, strategies
- Strategies: calling_station, tight_passive, tight_aggressive, loose_aggressive, pot_odds_player, bluffer, position_aware, gto_balanced

### Snakes and Ladders
- Endpoint: `/api/snakes-and-ladders/simulate`
- Configurable parameters: num_games, num_players, board_size, num_snakes, num_ladders, bounce_back

### Naughts and Crosses (Tic-Tac-Toe)
- Endpoint: `/api/naughts-and-crosses/simulate`
- Configurable parameters: num_games, board_size (3x3, 4x4, 5x5)

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── models/
│   ├── __init__.py
│   └── schemas.py         # Pydantic models for request/response
├── routers/
│   ├── __init__.py
│   ├── blackjack.py       # Blackjack endpoints
│   ├── poker.py           # Poker endpoints
│   ├── snakes_and_ladders.py
│   └── naughts_and_crosses.py
└── simulations/
    ├── __init__.py
    ├── blackjack_sim.py    # Blackjack simulation engine
    ├── poker_sim.py        # Poker simulation engine
    ├── snakes_and_ladders_sim.py
    └── naughts_and_crosses_sim.py
```

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
