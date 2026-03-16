import random
import statistics
from collections import defaultdict


# ─────────────────────────────────────────────────────────────────
#  SETTINGS — change these to customise your simulation
# ─────────────────────────────────────────────────────────────────

NUM_GAMES   = 10_000
NUM_PLAYERS = 2
BOARD_SIZE  = 34
NUM_SNAKES  = 5
NUM_LADDERS = 5
BOUNCE_BACK = True


# ─────────────────────────────────────────────────────────────────
#  PLAYER
#  Keeps track of where a player is and how many times they've rolled.
# ─────────────────────────────────────────────────────────────────

class Player:
    def __init__(self, number):
        # Players are just numbered — "Player 1", "Player 2", etc.
        self.name = f"Player {number}"
        self.position = 0
        self.rolls = 0

    def roll_dice(self):
        # Roll a standard six-sided die and count it
        self.rolls += 1
        return random.randint(1, 6)

    def move(self, steps):
        # Move forward by the rolled amount
        self.position += steps

        # Handle overshooting the end of the board
        if self.position > BOARD_SIZE:
            if BOUNCE_BACK:
                # Bounce back however many squares we overshot by
                overshoot = self.position - BOARD_SIZE
                self.position = BOARD_SIZE - overshoot
            else:
                # Just clamp to the final square and win
                self.position = BOARD_SIZE

    def has_won(self):
        return self.position == BOARD_SIZE

    def reset(self):
        # Send the player back to the start for the next game
        self.position = 0
        self.rolls = 0


# ─────────────────────────────────────────────────────────────────
#  BOARD
#  Randomly generates snakes and ladders, then checks if a position
#  triggers one when a player lands on it.
# ─────────────────────────────────────────────────────────────────

class Board:
    def __init__(self):
        # Snakes are stored as {head: tail} — land on the head, drop to the tail
        self.snakes = self._place_snakes()
        # Ladders are stored as {bottom: top} — land on the bottom, climb to the top
        self.ladders = self._place_ladders()

    def _place_snakes(self):
        snakes = {}
        while len(snakes) < NUM_SNAKES:
            head = random.randint(2, BOARD_SIZE - 1)
            tail = random.randint(1, head - 1)
            # Only add if this square isn't already a snake head
            if head not in snakes:
                snakes[head] = tail
        return snakes

    def _place_ladders(self):
        ladders = {}
        while len(ladders) < NUM_LADDERS:
            bottom = random.randint(1, BOARD_SIZE - 2)
            # Cap the top at BOARD_SIZE - 1 so a ladder can never carry you
            # straight to the finish — you still have to roll your way there
            top    = random.randint(bottom + 1, BOARD_SIZE - 1)
            # Skip squares already used by a snake or another ladder
            if bottom not in ladders and bottom not in self.snakes:
                ladders[bottom] = top
        return ladders

    def check_square(self, position):
        """
        Returns (new_position, event_type) after checking for snakes/ladders.
        event_type is "snake", "ladder", or None if nothing happened.
        """
        if position in self.snakes:
            return self.snakes[position], "snake"
        if position in self.ladders:
            return self.ladders[position], "ladder"
        return position, None


# ─────────────────────────────────────────────────────────────────
#  GAME
#  Runs a single game from start to finish and returns the results.
# ─────────────────────────────────────────────────────────────────

class Game:
    def __init__(self, players):
        # We receive the player list from outside so we can reuse them across games
        self.players = players
        self.board   = Board()

    def new_board(self):
        # Regenerate the board so each game has a fresh snake/ladder layout
        self.board = Board()

    def play(self):
        """
        Runs one full game. Returns a dict with everything that happened:
        who won, how many rolls each player took, and how many snakes/ladders
        each player hit.
        """
        # These track what happens during this one game
        snake_hits   = defaultdict(int)
        ladder_hits  = defaultdict(int)

        while True:
            for player in self.players:
                roll = player.roll_dice()
                player.move(roll)

                # Check if the square has a snake or ladder on it
                new_pos, event = self.board.check_square(player.position)
                player.position = new_pos

                if event == "snake":
                    snake_hits[player.name] += 1
                elif event == "ladder":
                    ladder_hits[player.name] += 1

                # First player to land on the final square wins
                if player.has_won():
                    return {
                        "winner":        player.name,
                        "winning_rolls": player.rolls,
                        # Copy the roll/event counts for every player at the moment the game ends
                        "rolls":         {p.name: p.rolls             for p in self.players},
                        "snake_hits":    {p.name: snake_hits[p.name]  for p in self.players},
                        "ladder_hits":   {p.name: ladder_hits[p.name] for p in self.players},
                    }


# ─────────────────────────────────────────────────────────────────
#  SIMULATION
#  Runs many games and builds up the stats we care about.
# ─────────────────────────────────────────────────────────────────

class Simulation:
    def __init__(self):
        # Build the player list — just numbered, no custom names needed
        self.players = [Player(i + 1) for i in range(NUM_PLAYERS)]
        self.game    = Game(self.players)

        # --- Stats we accumulate across all games ---

        # How many times each player won
        self.wins = defaultdict(int)

        # How many rolls each player took per game (list of ints per player)
        self.rolls_per_game = defaultdict(list)

        # Total snake and ladder hits per player
        self.total_snake_hits  = defaultdict(int)
        self.total_ladder_hits = defaultdict(int)

        # How long each game lasted (winner's roll count), used for the histogram
        self.game_lengths = []

    def run(self):
        """Play all the games one by one."""
        for _ in range(NUM_GAMES):
            # Reset players and get a new board before each game
            for p in self.players:
                p.reset()
            self.game.new_board()

            result = self.game.play()
            self._record(result)

    def _record(self, result):
        """Take the result dict from one game and fold it into our running totals."""
        self.wins[result["winner"]] += 1
        self.game_lengths.append(result["winning_rolls"])

        for name in result["rolls"]:
            self.rolls_per_game[name].append(result["rolls"][name])
            self.total_snake_hits[name]  += result["snake_hits"][name]
            self.total_ladder_hits[name] += result["ladder_hits"][name]

    # ─── Helper calculations ──────────────────────────────────────

    def _roll_stats(self, name):
        """Returns a bundle of roll statistics for one player."""
        rolls = self.rolls_per_game[name]
        return {
            "avg":    statistics.mean(rolls),
            "median": statistics.median(rolls),
            "min":    min(rolls),
            "max":    max(rolls),
            "stdev":  statistics.stdev(rolls) if len(rolls) > 1 else 0.0,
        }

    def _total_turns(self):
        """Total number of individual turns taken across all games and players."""
        return sum(sum(rolls) for rolls in self.rolls_per_game.values())

    # ─── Report ───────────────────────────────────────────────────

    def report(self):
        sep = "─" * 56

        print(f"\n{'═' * 56}")
        print(f"SNAKES & LADDERS SIMULATION REPORT")
        print(f"{'═' * 56}")
        print(f"  Games simulated : {NUM_GAMES:,}")
        print(f"  Players         : {NUM_PLAYERS}")
        print(f"  Board size      : {BOARD_SIZE}")
        print(f"  Bounce-back rule: {'on' if BOUNCE_BACK else 'off'}")

        # ── Overall game length ───────────────────────────────────
        print(f"\n{sep}")
        print("  GAME LENGTH  (winner's roll count)")
        print(sep)
        print(f"  Average  : {statistics.mean(self.game_lengths):.2f} rolls")
        print(f"  Median   : {statistics.median(self.game_lengths):.1f} rolls")
        print(f"  Shortest : {min(self.game_lengths)} rolls")
        print(f"  Longest  : {max(self.game_lengths)} rolls")

        # ── Per-player breakdown ──────────────────────────────────
        print(f"\n{sep}")
        print("  PER-PLAYER BREAKDOWN")
        print(sep)

        for player in self.players:
            name    = player.name
            rs      = self._roll_stats(name)
            win_pct = self.wins[name] / NUM_GAMES * 100

            print(f"\n  ▸ {name}")
            print(f"    Wins         : {self.wins[name]:,}  ({win_pct:.1f}%)")
            print(f"    Avg rolls    : {rs['avg']:.2f}")
            print(f"    Median rolls : {rs['median']:.1f}")
            print(f"    Min rolls    : {rs['min']}")
            print(f"    Max rolls    : {rs['max']}")
            print(f"    Std dev      : {rs['stdev']:.2f}")
            print(f"    Snake hits   : {self.total_snake_hits[name]:,}  "
                  f"({self.total_snake_hits[name] / NUM_GAMES:.2f} per game)")
            print(f"    Ladder hits  : {self.total_ladder_hits[name]:,}  "
                  f"({self.total_ladder_hits[name] / NUM_GAMES:.2f} per game)")

        # ── Board-wide totals ─────────────────────────────────────
        total_snakes  = sum(self.total_snake_hits.values())
        total_ladders = sum(self.total_ladder_hits.values())
        total_turns   = self._total_turns()

        print(f"\n{sep}")
        print("  BOARD EVENTS  (all players combined)")
        print(sep)
        print(f"  Total snake hits  : {total_snakes:,}  "
              f"(~1 every {total_turns / total_snakes:.1f} turns)")
        print(f"  Total ladder hits : {total_ladders:,}  "
              f"(~1 every {total_turns / total_ladders:.1f} turns)")

        # ── Histogram of game lengths ─────────────────────────────
        print(f"\n{sep}")
        print("  GAME LENGTH HISTOGRAM  (winner's rolls, buckets of 10)")
        print(sep)

        buckets = defaultdict(int)
        for length in self.game_lengths:
            bucket = (length // 10) * 10
            buckets[bucket] += 1

        max_count = max(buckets.values())
        bar_width = 30

        for bucket in sorted(buckets):
            count = buckets[bucket]
            bar   = "█" * int(count / max_count * bar_width)
            label = f"{bucket:>3}–{bucket + 9:<3}"
            print(f"  {label} | {bar:<{bar_width}} {count:,}")

        print(f"\n{'═' * 56}\n")


# ─────────────────────────────────────────────────────────────────
#  RUN IT
# ─────────────────────────────────────────────────────────────────

sim = Simulation()
sim.run()
sim.report()