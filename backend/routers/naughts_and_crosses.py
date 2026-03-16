"""Naughts and Crosses (Tic-Tac-Toe) API endpoints"""
from fastapi import APIRouter, HTTPException
from models.schemas import NaughtsAndCrossesConfig, NaughtsAndCrossesResults
from simulations import naughts_and_crosses_sim

router = APIRouter()


@router.post("/simulate", response_model=NaughtsAndCrossesResults)
async def simulate_naughts_and_crosses(config: NaughtsAndCrossesConfig):
    """
    Run a Naughts and Crosses (Tic-Tac-Toe) simulation with the specified configuration
    
    - **num_games**: Number of games to simulate (100-100,000)
    - **num_players**: Number of players (always 2)
    - **board_size**: Board size - 3x3, 4x4, or 5x5 (3-5)
    """
    try:
        config_dict = config.model_dump()
        results = naughts_and_crosses_sim.run_simulation(config_dict)
        return NaughtsAndCrossesResults(config=config, **results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
