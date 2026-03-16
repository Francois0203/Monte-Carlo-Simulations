"""
FastAPI backend for Monte Carlo Simulations
Provides endpoints for running statistical simulations with configurable parameters.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import blackjack, poker, snakes_and_ladders, naughts_and_crosses

app = FastAPI(
    title="Monte Carlo Simulations API",
    description="Run statistical simulations for various games with configurable parameters",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(blackjack.router, prefix="/api/blackjack", tags=["Blackjack"])
app.include_router(poker.router, prefix="/api/poker", tags=["Poker"])
app.include_router(snakes_and_ladders.router, prefix="/api/snakes-and-ladders", tags=["Snakes and Ladders"])
app.include_router(naughts_and_crosses.router, prefix="/api/naughts-and-crosses", tags=["Naughts and Crosses"])

@app.get("/")
async def root():
    return {
        "message": "Monte Carlo Simulations API",
        "version": "1.0.0",
        "endpoints": [
            "/api/blackjack/simulate",
            "/api/poker/simulate",
            "/api/snakes-and-ladders/simulate",
            "/api/naughts-and-crosses/simulate"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}