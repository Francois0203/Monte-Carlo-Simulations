import random
import statistics
from collections import defaultdict


# ─────────────────────────────────────────────────────────────────
#  SETTINGS — tweak these to change how the simulation runs
# ─────────────────────────────────────────────────────────────────

NUM_GAMES   = 10_000
NUM_PLAYERS = 2
BOARD_SIZE  = 3


# ─────────────────────────────────────────────────────────────────
#  BOARD
#  The grid lives here. Squares are numbered 0–8 like this:
#
#   0 | 1 | 2
#  ---+---+---
#   3 | 4 | 5
#  ---+---+---
#   6 | 7 | 8
#
#  An empty square holds None. A claimed square holds "X" or "O".
# ─────────────────────────────────────────────────────────────────

class Board:
    def __init__(self):
        # None means the square is empty
        self.squares = [None] * (BOARD_SIZE * BOARD_SIZE)

        # Pre-compute every winning line once — rows, columns, and both diagonals.
        # We'll check these after every move instead of recalculating each time.
        self.winning_lines = self._build_winning_lines()

    def _build_winning_lines(self):
        lines = []
        n = BOARD_SIZE

        # Rows — e.g. [0,1,2], [3,4,5], [6,7,8]
        for row in range(n):
            lines.append([row * n + col for col in range(n)])

        # Columns — e.g. [0,3,6], [1,4,7], [2,5,8]
        for col in range(n):
            lines.append([row * n + col for row in range(n)])

        # Top-left to bottom-right diagonal — e.g. [0,4,8]
        lines.append([i * n + i for i in range(n)])

        # Top-right to bottom-left diagonal — e.g. [2,4,6]
        lines.append([i * n + (n - 1 - i) for i in range(n)])

        return lines

    def available_squares(self):
        # Returns the indices of every square that hasn't been claimed yet
        return [i for i, val in enumerate(self.squares) if val is None]

    def place(self, square, symbol):
        self.squares[square] = symbol

    def check_winner(self):
        # Go through every possible winning line and see if one player owns all of it
        for line in self.winning_lines:
            values = [self.squares[i] for i in line]
            if values[0] is not None and all(v == values[0] for v in values):
                return values[0], line   # return the winning symbol and which line it was
        return None, None

    def is_full(self):
        return all(s is not None for s in self.squares)

    def reset(self):
        self.squares = [None] * (BOARD_SIZE * BOARD_SIZE)


# ─────────────────────────────────────────────────────────────────
#  PLAYER
#  Right now players pick moves completely at random — any open
#  square is equally likely. This is intentional: random play gives
#  us a clean statistical baseline.
# ─────────────────────────────────────────────────────────────────

class Player:
    def __init__(self, number, symbol):
        self.name   = f"Player {number}"
        self.symbol = symbol   # "X" or "O"

    def choose_square(self, board):
        # Pick a random empty square — no strategy, just probability
        return random.choice(board.available_squares())


# ─────────────────────────────────────────────────────────────────
#  GAME
#  Runs one full game of noughts & crosses and returns everything
#  that happened: who won, how many moves it took, which line won,
#  and which squares were played on.
# ─────────────────────────────────────────────────────────────────

class Game:
    def __init__(self):
        self.board   = Board()
        self.players = [Player(1, "X"), Player(2, "O")]

    def reset(self):
        self.board.reset()

    def play(self):
        # Track which squares were played, in order — useful for heatmaps
        move_sequence = []

        # Players alternate turns, starting with Player 1 (X)
        for move_number in range(BOARD_SIZE * BOARD_SIZE):
            # Alternate between the two players each turn
            player = self.players[move_number % 2]

            square = player.choose_square(self.board)
            self.board.place(square, player.symbol)
            move_sequence.append((player.name, square))

            # Check if this move just won the game
            winner_symbol, winning_line = self.board.check_winner()
            if winner_symbol is not None:
                return {
                    "winner":       player.name,
                    "symbol":       winner_symbol,
                    "moves":        move_number + 1,   # total moves played this game
                    "winning_line": tuple(winning_line),
                    "move_sequence": move_sequence,
                    "draw":         False,
                }

        # If we get here, the board is full and nobody won — it's a draw
        return {
            "winner":        None,
            "symbol":        None,
            "moves":         BOARD_SIZE * BOARD_SIZE,
            "winning_line":  None,
            "move_sequence": move_sequence,
            "draw":          True,
        }


# ─────────────────────────────────────────────────────────────────
#  SIMULATION
#  Plays NUM_GAMES games and rolls everything up into stats.
# ─────────────────────────────────────────────────────────────────

class Simulation:
    def __init__(self):
        self.game = Game()

        # Outcome counters
        self.wins  = defaultdict(int)   # wins per player name
        self.draws = 0

        # Move counts per game, split by outcome so we can compare
        self.moves_when_won  = defaultdict(list)   # per winner
        self.moves_all_games = []                  # every game regardless of outcome

        # Which winning lines came up most often — key is the tuple of square indices
        self.winning_line_counts = defaultdict(int)

        # How often each square was played on (across all games, all players)
        # This tells us which squares are "hottest"
        self.square_play_counts = defaultdict(int)

        # How often each square was the *first* move of a game
        self.first_move_counts = defaultdict(int)

        # Wins broken down by who went first (X always goes first)
        self.wins_going_first  = 0   # X wins
        self.wins_going_second = 0   # O wins

    def run(self):
        for _ in range(NUM_GAMES):
            self.game.reset()
            result = self.game.play()
            self._record(result)

    def _record(self, result):
        self.moves_all_games.append(result["moves"])

        # Track every square that was played during this game
        for i, (player_name, square) in enumerate(result["move_sequence"]):
            self.square_play_counts[square] += 1
            if i == 0:
                self.first_move_counts[square] += 1

        if result["draw"]:
            self.draws += 1
        else:
            winner = result["winner"]
            self.wins[winner] += 1
            self.moves_when_won[winner].append(result["moves"])
            self.winning_line_counts[result["winning_line"]] += 1

            if result["symbol"] == "X":
                self.wins_going_first += 1
            else:
                self.wins_going_second += 1

    # ─── Helpers ─────────────────────────────────────────────────

    def _describe_line(self, line):
        """Turn a tuple like (0,4,8) into a human-readable label."""
        n = BOARD_SIZE
        rows = {tuple(row * n + col for col in range(n)): f"Row {row + 1}"
                for row in range(n)}
        cols = {tuple(row * n + col for row in range(n)): f"Col {col + 1}"
                for col in range(n)}
        diag1 = tuple(i * n + i for i in range(n))
        diag2 = tuple(i * n + (n - 1 - i) for i in range(n))

        if line in rows:   return rows[line]
        if line in cols:   return cols[line]
        if line == diag1:  return "Diagonal (↘)"
        if line == diag2:  return "Diagonal (↙)"
        return str(line)

    def _avg(self, lst):
        return statistics.mean(lst) if lst else 0.0

    # ─── Report ───────────────────────────────────────────────────

    def report(self):
        sep = "─" * 56
        total_wins = sum(self.wins.values())

        print(f"\n{'═' * 56}")
        print(f"  ✕○  NOUGHTS & CROSSES SIMULATION REPORT")
        print(f"{'═' * 56}")
        print(f"  Games simulated : {NUM_GAMES:,}")
        print(f"  Board size      : {BOARD_SIZE}×{BOARD_SIZE}")
        print(f"  Move strategy   : random")

        # ── Outcomes ─────────────────────────────────────────────
        print(f"\n{sep}")
        print("  OUTCOMES")
        print(sep)
        print(f"  Player 1 (X) wins : {self.wins['Player 1']:,}  "
              f"({self.wins['Player 1'] / NUM_GAMES * 100:.1f}%)")
        print(f"  Player 2 (O) wins : {self.wins['Player 2']:,}  "
              f"({self.wins['Player 2'] / NUM_GAMES * 100:.1f}%)")
        print(f"  Draws             : {self.draws:,}  "
              f"({self.draws / NUM_GAMES * 100:.1f}%)")
        print(f"\n  Going first  (X) wins : {self.wins_going_first:,}  "
              f"({self.wins_going_first / total_wins * 100:.1f}% of all wins)")
        print(f"  Going second (O) wins : {self.wins_going_second:,}  "
              f"({self.wins_going_second / total_wins * 100:.1f}% of all wins)")

        # ── Game length ───────────────────────────────────────────
        print(f"\n{sep}")
        print("  GAME LENGTH  (total moves played)")
        print(sep)
        print(f"  Average  : {self._avg(self.moves_all_games):.2f} moves")
        print(f"  Shortest : {min(self.moves_all_games)} moves  "
              f"(minimum possible is {BOARD_SIZE * 2 - 1})")
        print(f"  Longest  : {max(self.moves_all_games)} moves  "
              f"(board has {BOARD_SIZE * BOARD_SIZE} squares)")

        # Average game length split by who won (or draw)
        p1_avg = self._avg(self.moves_when_won["Player 1"])
        p2_avg = self._avg(self.moves_when_won["Player 2"])
        print(f"\n  Avg moves when Player 1 wins : {p1_avg:.2f}")
        print(f"  Avg moves when Player 2 wins : {p2_avg:.2f}")

        # ── Winning lines ─────────────────────────────────────────
        print(f"\n{sep}")
        print("  MOST COMMON WINNING LINES")
        print(sep)
        sorted_lines = sorted(self.winning_line_counts.items(),
                              key=lambda x: x[1], reverse=True)
        for line, count in sorted_lines:
            label   = self._describe_line(line)
            squares = " → ".join(str(s) for s in line)
            pct     = count / total_wins * 100
            print(f"  {label:<18} squares [{squares}]  {count:,}  ({pct:.1f}%)")

        # ── Square heatmap ────────────────────────────────────────
        print(f"\n{sep}")
        print("  SQUARE HEATMAP  (how often each square was played)")
        print(sep)
        print("  (higher = more contested)\n")

        n = BOARD_SIZE
        # Find the max so we can show relative percentages
        max_plays = max(self.square_play_counts.values())

        for row in range(n):
            cells = []
            for col in range(n):
                idx   = row * n + col
                count = self.square_play_counts[idx]
                pct   = count / (NUM_GAMES * n * n) * 100  # as % of all possible plays
                cells.append(f" {pct:4.1f}% ")
            print("  " + "|".join(cells))
            if row < n - 1:
                print("  " + "+".join(["--------"] * n))

        # ── First move heatmap ────────────────────────────────────
        print(f"\n{sep}")
        print("  FIRST MOVE HEATMAP  (where Player 1 tends to open)")
        print(sep)
        print("  (higher = more popular opening square)\n")

        for row in range(n):
            cells = []
            for col in range(n):
                idx   = row * n + col
                count = self.first_move_counts[idx]
                pct   = count / NUM_GAMES * 100
                cells.append(f" {pct:4.1f}% ")
            print("  " + "|".join(cells))
            if row < n - 1:
                print("  " + "+".join(["--------"] * n))

        print(f"\n{'═' * 56}\n")


# ─────────────────────────────────────────────────────────────────
#  RUN IT
# ─────────────────────────────────────────────────────────────────

sim = Simulation()
sim.run()
sim.report()