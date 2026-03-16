"""Poker API endpoints"""
from fastapi import APIRouter, HTTPException
from models.schemas import PokerConfig, PokerResults
from simulations import poker_sim

router = APIRouter()


@router.post("/simulate", response_model=PokerResults)
async def simulate_poker(config: PokerConfig):
    """
    Run a Poker simulation with the specified configuration
    
    - **num_hands**: Number of hands to simulate (100-100,000)
    - **num_players**: Number of players at the table (2-9)
    - **small_blind**: Small blind amount
    - **big_blind**: Big blind amount
    - **starting_stack**: Starting chip stack per player
    - **allow_rebuys**: Allow rebuys when players bust
    - **players**: List of player strategies to simulate
    """
    try:
        config_dict = config.model_dump()
        results = poker_sim.run_simulation(config_dict)
        return PokerResults(config=config, **results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies")
async def get_strategies():
    """Get available player strategies"""
    return {
        "strategies": [
            "calling_station",
            "tight_passive",
            "tight_aggressive",
            "loose_aggressive",
            "pot_odds_player",
            "bluffer",
            "position_aware",
            "gto_balanced"
        ],
        "descriptions": {
            "calling_station": "Calls almost everything, rarely raises",
            "tight_passive": "Only plays strong hands, but just calls",
            "tight_aggressive": "Strong hand selection + bets and raises",
            "loose_aggressive": "Plays many hands, applies constant pressure",
            "pot_odds_player": "Calls/folds based on pot odds vs equity",
            "bluffer": "Wide range, high bluff frequency",
            "position_aware": "Adjusts play based on table position",
            "gto_balanced": "Game-theory optimal mixed strategy"
        }
    }
