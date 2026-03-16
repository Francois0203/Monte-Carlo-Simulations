"""Blackjack API endpoints"""
from fastapi import APIRouter, HTTPException
from models.schemas import BlackjackConfig, BlackjackResults
from simulations import blackjack_sim

router = APIRouter()


@router.post("/simulate", response_model=BlackjackResults)
async def simulate_blackjack(config: BlackjackConfig):
    """
    Run a Blackjack simulation with the specified configuration
    
    - **num_games**: Number of games to simulate (100-100,000)
    - **num_decks**: Number of decks in the shoe (1-8)
    - **blackjack_payout**: Payout multiplier for blackjack (1.0-2.0)
    - **dealer_stands_soft**: Whether dealer stands on soft 17
    - **allow_splits**: Allow splitting pairs
    - **allow_double_down**: Allow doubling down
    - **ace_high**: Ace can count as 1 or 11
    - **players**: List of player strategies to simulate
    """
    try:
        config_dict = config.model_dump()
        results = blackjack_sim.run_simulation(config_dict)
        return BlackjackResults(config=config, **results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies")
async def get_strategies():
    """Get available player strategies"""
    return {
        "strategies": list(blackjack_sim.STRATEGIES.keys()),
        "descriptions": {
            "never_bust": "Stand on any 12+ to never risk busting",
            "safe": "Minimal risk strategy, stand early",
            "basic": "Mathematically optimal play (Basic Strategy)",
            "aggressive": "High-risk, high-reward strategy",
            "mimic_dealer": "Copy dealer's rules exactly",
            "gut_feel": "Typical uninformed player",
            "card_counter": "Basic strategy + bet scaling based on count",
            "martingale": "Basic strategy + double bet after losses"
        }
    }
