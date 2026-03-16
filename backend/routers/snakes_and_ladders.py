"""Snakes and Ladders API endpoints"""
from fastapi import APIRouter, HTTPException
from models.schemas import SnakesAndLaddersConfig, SnakesAndLaddersResults
from simulations import snakes_and_ladders_sim

router = APIRouter()


@router.post("/simulate", response_model=SnakesAndLaddersResults)
async def simulate_snakes_and_ladders(config: SnakesAndLaddersConfig):
    """
    Run a Snakes and Ladders simulation with the specified configuration
    
    - **num_games**: Number of games to simulate (100-100,000)
    - **num_players**: Number of players (2-6)
    - **board_size**: Number of squares on the board (20-100)
    - **num_snakes**: Number of snakes on the board (0-20)
    - **num_ladders**: Number of ladders on the board (0-20)
    - **bounce_back**: Bounce back when overshooting the final square
    """
    try:
        config_dict = config.model_dump()
        results = snakes_and_ladders_sim.run_simulation(config_dict)
        return SnakesAndLaddersResults(config=config, **results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
