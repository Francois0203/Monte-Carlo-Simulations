"""Pydantic models for Blackjack simulation"""
from typing import List, Dict
from pydantic import BaseModel, Field


class BlackjackConfig(BaseModel):
    """Configuration for Blackjack simulation"""
    num_games: int = Field(default=10000, ge=100, le=100000, description="Number of games to simulate")
    num_decks: int = Field(default=6, ge=1, le=8, description="Number of decks in the shoe")
    blackjack_payout: float = Field(default=1.5, ge=1.0, le=2.0, description="Blackjack payout multiplier (3:2 = 1.5)")
    dealer_stands_soft: bool = Field(default=True, description="Dealer stands on soft 17")
    allow_splits: bool = Field(default=True, description="Allow splitting pairs")
    allow_double_down: bool = Field(default=True, description="Allow doubling down")
    ace_high: bool = Field(default=True, description="Ace can count as 1 or 11")
    players: List[str] = Field(
        default=["never_bust", "safe", "basic", "aggressive", "mimic_dealer", "gut_feel", "card_counter", "martingale"],
        description="List of player strategies to simulate"
    )


class PlayerStats(BaseModel):
    """Statistics for a single player strategy"""
    name: str
    strategy: str
    games_played: int
    wins: int
    losses: int
    pushes: int
    blackjacks: int
    busts: int
    win_rate: float
    average_payout: float
    total_wagered: float
    total_won: float
    net_profit: float
    roi: float


class BlackjackResults(BaseModel):
    """Results from Blackjack simulation"""
    config: BlackjackConfig
    player_stats: List[PlayerStats]
    total_games: int
    total_hands: int
    dealer_busts: int
    dealer_bust_rate: float
    execution_time: float


class PokerConfig(BaseModel):
    """Configuration for Poker simulation"""
    num_hands: int = Field(default=10000, ge=100, le=100000, description="Number of hands to simulate")
    num_players: int = Field(default=6, ge=2, le=9, description="Number of players at the table")
    small_blind: int = Field(default=1, ge=1, le=100, description="Small blind amount")
    big_blind: int = Field(default=2, ge=2, le=200, description="Big blind amount")
    starting_stack: int = Field(default=200, ge=50, le=10000, description="Starting chip stack per player")
    allow_rebuys: bool = Field(default=True, description="Allow rebuys when players bust")
    players: List[str] = Field(
        default=["calling_station", "tight_passive", "tight_aggressive", "loose_aggressive", "pot_odds_player", "bluffer", "position_aware", "gto_balanced"],
        description="List of player strategies to simulate"
    )


class PokerPlayerStats(BaseModel):
    """Statistics for a poker player strategy"""
    name: str
    strategy: str
    hands_played: int
    hands_won: int
    total_winnings: float
    total_losses: float
    net_profit: float
    win_rate: float
    vpip: float  # Voluntarily Put money In Pot
    pfr: float   # Pre-Flop Raise
    avg_pot_won: float
    biggest_pot: float


class PokerResults(BaseModel):
    """Results from Poker simulation"""
    config: PokerConfig
    player_stats: List[PokerPlayerStats]
    total_hands: int
    total_pots: int
    average_pot_size: float
    execution_time: float


class SnakesAndLaddersConfig(BaseModel):
    """Configuration for Snakes and Ladders simulation"""
    num_games: int = Field(default=10000, ge=100, le=100000, description="Number of games to simulate")
    num_players: int = Field(default=2, ge=2, le=6, description="Number of players")
    board_size: int = Field(default=34, ge=20, le=100, description="Number of squares on the board")
    num_snakes: int = Field(default=5, ge=0, le=20, description="Number of snakes on the board")
    num_ladders: int = Field(default=5, ge=0, le=20, description="Number of ladders on the board")
    bounce_back: bool = Field(default=True, description="Bounce back when overshooting the final square")


class SnakesAndLaddersPlayerStats(BaseModel):
    """Statistics for a Snakes and Ladders player"""
    name: str
    wins: int
    win_rate: float
    average_rolls: float
    min_rolls: int
    max_rolls: int
    average_snakes_hit: float
    average_ladders_hit: float


class SnakesAndLaddersResults(BaseModel):
    """Results from Snakes and Ladders simulation"""
    config: SnakesAndLaddersConfig
    player_stats: List[SnakesAndLaddersPlayerStats]
    total_games: int
    average_game_length: float
    shortest_game: int
    longest_game: int
    execution_time: float


class NaughtsAndCrossesConfig(BaseModel):
    """Configuration for Naughts and Crosses (Tic-Tac-Toe) simulation"""
    num_games: int = Field(default=10000, ge=100, le=100000, description="Number of games to simulate")
    num_players: int = Field(default=2, ge=2, le=2, description="Number of players (always 2)")
    board_size: int = Field(default=3, ge=3, le=5, description="Board size (3x3, 4x4, or 5x5)")


class NaughtsAndCrossesPlayerStats(BaseModel):
    """Statistics for a Naughts and Crosses player"""
    name: str
    symbol: str
    wins: int
    losses: int
    draws: int
    win_rate: float
    loss_rate: float
    draw_rate: float


class NaughtsAndCrossesResults(BaseModel):
    """Results from Naughts and Crosses simulation"""
    config: NaughtsAndCrossesConfig
    player_stats: List[NaughtsAndCrossesPlayerStats]
    total_games: int
    total_wins_x: int
    total_wins_o: int
    total_draws: int
    draw_rate: float
    average_moves_per_game: float
    execution_time: float
