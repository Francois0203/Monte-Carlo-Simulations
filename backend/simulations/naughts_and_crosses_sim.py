"""
Naughts and Crosses (Tic-Tac-Toe) Monte Carlo Simulation
Refactored for FastAPI backend with configurable parameters
"""
import random
import time
from collections import defaultdict
from typing import List, Dict, Any, Optional, Tuple


class Board:
    """The game board"""
    def __init__(self, size: int = 3):
        self.size = size
        self.squares = [None] * (size * size)
        self.winning_lines = self._build_winning_lines()
    
    def _build_winning_lines(self) -> List[List[int]]:
        """Build all possible winning lines"""
        lines = []
        n = self.size
        
        # Rows
        for row in range(n):
            lines.append([row * n + col for col in range(n)])
        
        # Columns
        for col in range(n):
            lines.append([row * n + col for row in range(n)])
        
        # Diagonals
        lines.append([i * n + i for i in range(n)])
        lines.append([i * n + (n - 1 - i) for i in range(n)])
        
        return lines
    
    def available_squares(self) -> List[int]:
        """Get all available squares"""
        return [i for i, val in enumerate(self.squares) if val is None]
    
    def place(self, square: int, symbol: str):
        """Place a symbol on the board"""
        self.squares[square] = symbol
    
    def check_winner(self) -> Tuple[Optional[str], Optional[List[int]]]:
        """Check if there's a winner"""
        for line in self.winning_lines:
            values = [self.squares[i] for i in line]
            if values[0] is not None and all(v == values[0] for v in values):
                return values[0], line
        return None, None
    
    def is_full(self) -> bool:
        """Check if board is full"""
        return all(s is not None for s in self.squares)
    
    def reset(self):
        """Reset the board"""
        self.squares = [None] * (self.size * self.size)


class Player:
    """A player in the game"""
    def __init__(self, number: int, symbol: str):
        self.name = f"Player {number}"
        self.symbol = symbol
    
    def choose_square(self, board: Board) -> int:
        """Choose a square (random for Monte Carlo simulation)"""
        return random.choice(board.available_squares())


def run_simulation(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the Naughts and Crosses simulation
    
    Args:
        config: Dictionary with simulation parameters
        
    Returns:
        Dictionary with simulation results
    """
    start_time = time.time()
    
    # Extract config
    num_games = config.get('num_games', 10000)
    board_size = config.get('board_size', 3)
    
    # Initialize game
    board = Board(board_size)
    players = [Player(1, "X"), Player(2, "O")]
    
    # Statistics tracking
    wins = defaultdict(int)
    draws = 0
    moves_per_game = []
    winning_line_counts = defaultdict(int)
    square_play_counts = defaultdict(int)
    first_move_counts = defaultdict(int)
    wins_going_first = 0
    wins_going_second = 0
    
    # Run simulation
    for _ in range(num_games):
        board.reset()
        move_sequence = []
        
        # Play one game
        for move_number in range(board_size * board_size):
            player = players[move_number % 2]
            
            square = player.choose_square(board)
            board.place(square, player.symbol)
            move_sequence.append((player.name, square))
            
            # Track square usage
            square_play_counts[square] += 1
            if move_number == 0:
                first_move_counts[square] += 1
            
            # Check for winner
            winner_symbol, winning_line = board.check_winner()
            if winner_symbol is not None:
                wins[player.name] += 1
                moves_per_game.append(move_number + 1)
                winning_line_counts[tuple(winning_line)] += 1
                
                if player.symbol == "X":
                    wins_going_first += 1
                else:
                    wins_going_second += 1
                break
        else:
            # No winner - draw
            draws += 1
            moves_per_game.append(board_size * board_size)
    
    # Calculate statistics
    player_stats = []
    for player in players:
        name = player.name
        symbol = player.symbol
        win_count = wins[name]
        loss_count = wins[players[1].name] if player == players[0] else wins[players[0].name]
        
        win_rate = win_count / num_games if num_games > 0 else 0
        loss_rate = loss_count / num_games if num_games > 0 else 0
        draw_rate = draws / num_games if num_games > 0 else 0
        
        player_stats.append({
            "name": name,
            "symbol": symbol,
            "wins": win_count,
            "losses": loss_count,
            "draws": draws,
            "win_rate": round(win_rate, 4),
            "loss_rate": round(loss_rate, 4),
            "draw_rate": round(draw_rate, 4),
        })
    
    execution_time = time.time() - start_time
    avg_moves = sum(moves_per_game) / len(moves_per_game) if moves_per_game else 0
    draw_rate = draws / num_games if num_games > 0 else 0
    
    return {
        "player_stats": player_stats,
        "total_games": num_games,
        "total_wins_x": wins_going_first,
        "total_wins_o": wins_going_second,
        "total_draws": draws,
        "draw_rate": round(draw_rate, 4),
        "average_moves_per_game": round(avg_moves, 2),
        "execution_time": round(execution_time, 2),
    }
