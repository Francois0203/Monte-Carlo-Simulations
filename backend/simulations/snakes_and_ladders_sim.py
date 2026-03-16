"""
Snakes and Ladders Monte Carlo Simulation
Refactored for FastAPI backend with configurable parameters
"""
import random
import time
from collections import defaultdict
from typing import List, Dict, Any


class Player:
    """Represents a player in the game"""
    def __init__(self, number: int):
        self.name = f"Player {number}"
        self.position = 0
        self.rolls = 0
        self.snakes_hit = 0
        self.ladders_hit = 0
    
    def roll_dice(self) -> int:
        """Roll a six-sided die"""
        self.rolls += 1
        return random.randint(1, 6)
    
    def move(self, steps: int, board_size: int, bounce_back: bool):
        """Move the player"""
        self.position += steps
        
        if self.position > board_size:
            if bounce_back:
                overshoot = self.position - board_size
                self.position = board_size - overshoot
            else:
                self.position = board_size
    
    def has_won(self, board_size: int) -> bool:
        """Check if player has won"""
        return self.position == board_size
    
    def reset(self):
        """Reset for next game"""
        self.position = 0
        self.rolls = 0
        self.snakes_hit = 0
        self.ladders_hit = 0


class Board:
    """The game board with snakes and ladders"""
    def __init__(self, board_size: int, num_snakes: int, num_ladders: int):
        self.board_size = board_size
        self.snakes = self._place_snakes(num_snakes)
        self.ladders = self._place_ladders(num_ladders)
    
    def _place_snakes(self, num_snakes: int) -> Dict[int, int]:
        """Place snakes on the board"""
        snakes = {}
        attempts = 0
        while len(snakes) < num_snakes and attempts < num_snakes * 10:
            head = random.randint(2, self.board_size - 1)
            tail = random.randint(1, head - 1)
            if head not in snakes:
                snakes[head] = tail
            attempts += 1
        return snakes
    
    def _place_ladders(self, num_ladders: int) -> Dict[int, int]:
        """Place ladders on the board"""
        ladders = {}
        attempts = 0
        while len(ladders) < num_ladders and attempts < num_ladders * 10:
            bottom = random.randint(1, self.board_size - 2)
            top = random.randint(bottom + 1, self.board_size - 1)
            if bottom not in ladders and bottom not in self.snakes:
                ladders[bottom] = top
            attempts += 1
        return ladders
    
    def check_square(self, position: int) -> tuple:
        """Check if position has a snake or ladder"""
        if position in self.snakes:
            return self.snakes[position], "snake"
        if position in self.ladders:
            return self.ladders[position], "ladder"
        return position, None


def run_simulation(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the Snakes and Ladders simulation
    
    Args:
        config: Dictionary with simulation parameters
        
    Returns:
        Dictionary with simulation results
    """
    start_time = time.time()
    
    # Extract config
    num_games = config.get('num_games', 10000)
    num_players = config.get('num_players', 2)
    board_size = config.get('board_size', 34)
    num_snakes = config.get('num_snakes', 5)
    num_ladders = config.get('num_ladders', 5)
    bounce_back = config.get('bounce_back', True)
    
    # Initialize players
    players = [Player(i + 1) for i in range(num_players)]
    
    # Statistics tracking
    wins = defaultdict(int)
    rolls_per_game = defaultdict(list)
    snakes_per_game = defaultdict(list)
    ladders_per_game = defaultdict(list)
    game_lengths = []
    
    # Run simulation
    for _ in range(num_games):
        # Reset players and create new board
        for p in players:
            p.reset()
        board = Board(board_size, num_snakes, num_ladders)
        
        # Play one game
        while True:
            for player in players:
                roll = player.roll_dice()
                player.move(roll, board_size, bounce_back)
                
                # Check for snakes/ladders
                new_pos, event = board.check_square(player.position)
                player.position = new_pos
                
                if event == "snake":
                    player.snakes_hit += 1
                elif event == "ladder":
                    player.ladders_hit += 1
                
                # Check for winner
                if player.has_won(board_size):
                    wins[player.name] += 1
                    game_lengths.append(player.rolls)
                    
                    # Record stats for all players
                    for p in players:
                        rolls_per_game[p.name].append(p.rolls)
                        snakes_per_game[p.name].append(p.snakes_hit)
                        ladders_per_game[p.name].append(p.ladders_hit)
                    
                    break
            else:
                continue
            break
    
    # Calculate statistics
    player_stats = []
    for player in players:
        name = player.name
        win_count = wins[name]
        win_rate = win_count / num_games if num_games > 0 else 0
        
        rolls = rolls_per_game[name]
        snakes = snakes_per_game[name]
        ladders = ladders_per_game[name]
        
        player_stats.append({
            "name": name,
            "wins": win_count,
            "win_rate": round(win_rate, 4),
            "average_rolls": round(sum(rolls) / len(rolls), 2) if rolls else 0,
            "min_rolls": min(rolls) if rolls else 0,
            "max_rolls": max(rolls) if rolls else 0,
            "average_snakes_hit": round(sum(snakes) / len(snakes), 2) if snakes else 0,
            "average_ladders_hit": round(sum(ladders) / len(ladders), 2) if ladders else 0,
        })
    
    execution_time = time.time() - start_time
    avg_game_length = sum(game_lengths) / len(game_lengths) if game_lengths else 0
    
    return {
        "player_stats": player_stats,
        "total_games": num_games,
        "average_game_length": round(avg_game_length, 2),
        "shortest_game": min(game_lengths) if game_lengths else 0,
        "longest_game": max(game_lengths) if game_lengths else 0,
        "execution_time": round(execution_time, 2),
    }
