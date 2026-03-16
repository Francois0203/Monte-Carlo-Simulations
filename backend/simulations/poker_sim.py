"""
Poker Monte Carlo Simulation (Simplified for statistical analysis)
Refactored for FastAPI backend with configurable parameters
"""
import random
import time
from collections import defaultdict
from typing import List, Dict, Any, Tuple
from itertools import combinations


# Hand rankings
HIGH_CARD = 0
ONE_PAIR = 1
TWO_PAIR = 2
THREE_OF_A_KIND = 3
STRAIGHT = 4
FLUSH = 5
FULL_HOUSE = 6
FOUR_OF_A_KIND = 7
STRAIGHT_FLUSH = 8
ROYAL_FLUSH = 9

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['♠', '♥', '♦', '♣']
RANK_VAL = {r: i for i, r in enumerate(RANKS)}


def make_deck() -> List[Tuple[str, str]]:
    """Create a standard deck"""
    return [(r, s) for s in SUITS for r in RANKS]


def rank_val(card: Tuple[str, str]) -> int:
    """Get numeric value of card rank"""
    return RANK_VAL[card[0]]


def evaluate_hand(cards: List[Tuple[str, str]]) -> Tuple[int, Tuple]:
    """Evaluate the best 5-card poker hand from up to 7 cards"""
    if len(cards) < 5:
        return (-1, ())
    
    best = (-1, ())
    for combo in combinations(cards, 5):
        score = score_five(list(combo))
        if score > best:
            best = score
    return best


def score_five(cards: List[Tuple[str, str]]) -> Tuple[int, Tuple]:
    """Score exactly 5 cards"""
    vals = sorted([rank_val(c) for c in cards], reverse=True)
    suits = [c[1] for c in cards]
    
    is_flush = len(set(suits)) == 1
    is_straight = _is_straight(vals)
    
    # Count occurrences
    counts = defaultdict(int)
    for v in vals:
        counts[v] += 1
    
    freq = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
    grouped = [v for v, _ in freq]
    cnt = [c for _, c in freq]
    
    if is_straight and is_flush:
        if vals[0] == 12:  # Ace-high
            return (ROYAL_FLUSH, tuple(vals))
        return (STRAIGHT_FLUSH, tuple(vals))
    if cnt[0] == 4:
        return (FOUR_OF_A_KIND, tuple(grouped))
    if cnt[0] == 3 and cnt[1] == 2:
        return (FULL_HOUSE, tuple(grouped))
    if is_flush:
        return (FLUSH, tuple(vals))
    if is_straight:
        return (STRAIGHT, tuple(vals))
    if cnt[0] == 3:
        return (THREE_OF_A_KIND, tuple(grouped))
    if cnt[0] == 2 and cnt[1] == 2:
        return (TWO_PAIR, tuple(grouped))
    if cnt[0] == 2:
        return (ONE_PAIR, tuple(grouped))
    return (HIGH_CARD, tuple(vals))


def _is_straight(sorted_vals: List[int]) -> bool:
    """Check if values form a straight"""
    if sorted_vals[0] - sorted_vals[4] == 4 and len(set(sorted_vals)) == 5:
        return True
    # Wheel: A-2-3-4-5
    if sorted_vals == [12, 3, 2, 1, 0]:
        return True
    return False


class Player:
    """A poker player"""
    def __init__(self, name: str, strategy: str, starting_stack: int):
        self.name = name
        self.strategy = strategy
        self.stack = starting_stack
        self.starting_stack = starting_stack
        self.hands_played = 0
        self.hands_won = 0
        self.total_winnings = 0
        self.total_losses = 0
        self.vpip_count = 0  # Voluntarily put money in pot
        self.pfr_count = 0   # Pre-flop raise
        self.pots_won = []
    
    def reset_stack(self):
        """Reset stack to starting amount"""
        self.stack = self.starting_stack
    
    def can_play(self) -> bool:
        """Check if player has chips"""
        return self.stack > 0


def run_simulation(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run simplified poker simulation
    
    Args:
        config: Dictionary with simulation parameters
        
    Returns:
        Dictionary with simulation results
    """
    start_time = time.time()
    
    # Extract configuration and ensure integers
    num_hands = int(config.get('num_hands', 1000))
    num_players = int(config.get('num_players', 6))
    small_blind = int(config.get('small_blind', 1))
    big_blind = int(config.get('big_blind', 2))
    starting_stack = int(config.get('starting_stack', 200))
    allow_rebuys = config.get('allow_rebuys', True)
    player_strategies = config.get('players', ["tight_aggressive"] * num_players)
    
    # Create players
    players = []
    for i in range(min(num_players, len(player_strategies))):
        strategy = player_strategies[i] if i < len(player_strategies) else "tight_aggressive"
        players.append(Player(f"Player {i+1} ({strategy})", strategy, starting_stack))
    
    # Statistics
    total_pots = 0
    pot_sizes = []
    
    # Simplifiedsimulation - each hand, random players compete
    for hand_num in range(num_hands):
        # Ensure all players have chips
        active_players = [p for p in players if p.can_play()]
        if len(active_players) < 2:
            if allow_rebuys:
                for p in players:
                    if not p.can_play():
                        p.reset_stack()
                active_players = players
            else:
                break
        
        # Simplified hand simulation
        deck = make_deck()
        random.shuffle(deck)
        
        # Deal hole cards
        hole_cards = {}
        for i, player in enumerate(active_players[:min(len(active_players), 9)]):
            hole_cards[player] = [deck.pop(), deck.pop()]
            player.hands_played += 1
        
        # Community cards
        community = [deck.pop() for _ in range(5)]
        
        # Simple pot calculation
        pot = small_blind + big_blind
        pot_contribution = {p: 0 for p in hole_cards.keys()}
        
        # Simplified betting - each player contributes based on strategy
        for player in hole_cards.keys():
            # Simplified: tight strategies play fewer hands
            play_chance = {
                "tight_passive": 0.3,
                "tight_aggressive": 0.35,
                "loose_aggressive": 0.6,
                "calling_station": 0.7,
                "pot_odds_player": 0.4,
                "bluffer": 0.5,
                "position_aware": 0.4,
                "gto_balanced": 0.4,
            }.get(player.strategy, 0.4)
            
            if random.random() < play_chance:
                max_contrib = int(min(player.stack, big_blind * 5))
                contribution = random.randint(big_blind, max(big_blind, max_contrib))
                pot += contribution
                pot_contribution[player] = contribution
                player.stack -= contribution
                player.vpip_count += 1
        
        # Evaluate hands
        hand_scores = {}
        for player, hole in hole_cards.items():
            if pot_contribution[player] > 0:  # Player is still in
                score = evaluate_hand(hole + community)
                hand_scores[player] = score
        
        if hand_scores:
            # Find winner(s)
            max_score = max(hand_scores.values())
            winners = [p for p, s in hand_scores.items() if s == max_score]
            winnings_per_player = pot / len(winners)
            
            for winner in winners:
                winner.hands_won += 1
                winner.stack += winnings_per_player
                winner.total_winnings += winnings_per_player
                winner.pots_won.append(pot)
            
            # Track losses
            for player, contribution in pot_contribution.items():
                if player not in winners and contribution > 0:
                    player.total_losses += contribution
        
        total_pots += 1
        pot_sizes.append(pot)
    
    # Calculate statistics
    player_stats = []
    for player in players:
        hands = player.hands_played
        vpip = (player.vpip_count / hands * 100) if hands > 0 else 0
        win_rate = (player.hands_won / hands * 100) if hands > 0 else 0
        net_profit = player.stack - player.starting_stack
        avg_pot_won = (sum(player.pots_won) / len(player.pots_won)) if player.pots_won else 0
        biggest_pot = max(player.pots_won) if player.pots_won else 0
        
        player_stats.append({
            "name": player.name,
            "strategy": player.strategy,
            "hands_played": hands,
            "hands_won": player.hands_won,
            "total_winnings": round(player.total_winnings, 2),
            "total_losses": round(player.total_losses, 2),
            "net_profit": round(net_profit, 2),
            "win_rate": round(win_rate, 2),
            "vpip": round(vpip, 2),
            "pfr": round((player.pfr_count / hands * 100) if hands > 0 else 0, 2),
            "avg_pot_won": round(avg_pot_won, 2),
            "biggest_pot": round(biggest_pot, 2),
        })
    
    execution_time = time.time() - start_time
    avg_pot_size = sum(pot_sizes) / len(pot_sizes) if pot_sizes else 0
    
    return {
        "player_stats": player_stats,
        "total_hands": num_hands,
        "total_pots": total_pots,
        "average_pot_size": round(avg_pot_size, 2),
        "execution_time": round(execution_time, 2),
    }
