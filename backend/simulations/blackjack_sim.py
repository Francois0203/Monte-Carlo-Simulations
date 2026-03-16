"""
Blackjack Monte Carlo Simulation
Refactored for FastAPI backend with configurable parameters
"""
import random
import time
from collections import defaultdict
from typing import List, Dict, Any, Tuple


class Card:
    """Represents a playing card"""
    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit
    
    def value(self, ace_high: bool = True) -> int:
        """Get the value of the card"""
        if self.rank in ('J', 'Q', 'K'):
            return 10
        if self.rank == 'A':
            return 11 if ace_high else 1
        return int(self.rank)


class Hand:
    """Represents a hand of cards"""
    def __init__(self, cards: List[Card], ace_high: bool = True):
        self.cards = cards
        self.ace_high = ace_high
    
    def value(self) -> int:
        """Calculate the best value for the hand"""
        total = sum(card.value(self.ace_high) for card in self.cards)
        if self.ace_high:
            aces = sum(1 for card in self.cards if card.rank == 'A')
            while total > 21 and aces:
                total -= 10
                aces -= 1
        return total
    
    def is_soft(self) -> bool:
        """Check if hand has an Ace counted as 11"""
        if not self.ace_high:
            return False
        total = sum(card.value(self.ace_high) for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == 'A')
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return aces > 0 and total <= 21
    
    def is_blackjack(self) -> bool:
        """Check if hand is a natural blackjack"""
        return len(self.cards) == 2 and self.value() == 21
    
    def is_pair(self) -> bool:
        """Check if hand is a pair"""
        return len(self.cards) == 2 and self.cards[0].value(self.ace_high) == self.cards[1].value(self.ace_high)


class Shoe:
    """The deck shoe containing multiple decks"""
    def __init__(self, num_decks: int = 6):
        self.num_decks = num_decks
        self.running_count = 0
        self.reshuffle()
    
    def reshuffle(self):
        """Shuffle the shoe"""
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['♠', '♥', '♦', '♣']
        self.cards = [Card(rank, suit) for _ in range(self.num_decks) for suit in suits for rank in ranks]
        random.shuffle(self.cards)
        self.reshuffle_point = len(self.cards) // 4
        self.running_count = 0
    
    def draw(self) -> Card:
        """Draw a card from the shoe"""
        if len(self.cards) <= self.reshuffle_point:
            self.reshuffle()
        card = self.cards.pop()
        # Update running count for card counting
        val = card.value()
        if 2 <= val <= 6:
            self.running_count += 1
        elif val >= 10:
            self.running_count -= 1
        return card
    
    def true_count(self) -> float:
        """Calculate true count for card counting"""
        decks_remaining = max(0.5, len(self.cards) / 52)
        return self.running_count / decks_remaining
    
    def deal_hand(self, ace_high: bool = True) -> Hand:
        """Deal a new hand"""
        return Hand([self.draw(), self.draw()], ace_high)


class Strategy:
    """Base strategy class"""
    @staticmethod
    def decide(hand: Hand, dealer_upcard_rank: str, can_double: bool, can_split: bool, config: Dict) -> str:
        """Decide what action to take"""
        raise NotImplementedError


class NeverBustStrategy(Strategy):
    """Stand on any 12+ to never risk busting"""
    @staticmethod
    def decide(hand: Hand, dealer_upcard_rank: str, can_double: bool, can_split: bool, config: Dict) -> str:
        return "stand" if hand.value() >= 12 else "hit"


class SafeStrategy(Strategy):
    """Minimal risk strategy"""
    @staticmethod
    def decide(hand: Hand, dealer_upcard_rank: str, can_double: bool, can_split: bool, config: Dict) -> str:
        total = hand.value()
        dealer_val = Card(dealer_upcard_rank, '♠').value(config.get('ace_high', True))
        
        if can_split and hand.is_pair():
            if hand.cards[0].value(config.get('ace_high', True)) == 11:
                return "split"
        
        if can_double and total == 11 and dealer_val <= 6:
            return "double"
        
        if total >= 13:
            return "stand"
        
        return "hit"


class BasicStrategy(Strategy):
    """Mathematically optimal play"""
    @staticmethod
    def decide(hand: Hand, dealer_upcard_rank: str, can_double: bool, can_split: bool, config: Dict) -> str:
        total = hand.value()
        soft = hand.is_soft()
        dealer_val = Card(dealer_upcard_rank, '♠').value(config.get('ace_high', True))
        
        if can_split and hand.is_pair():
            pv = hand.cards[0].value(config.get('ace_high', True))
            if pv == 11: return "split"
            if pv == 8: return "split"
            if pv == 10: return "stand"
            if pv == 5: return "double" if can_double and dealer_val <= 9 else "hit"
            if pv == 4: return "split" if dealer_val in (5, 6) else "hit"
            if pv == 9: return "stand" if dealer_val in (7, 10, 11) else "split"
            if pv in (2, 3, 7): return "split" if dealer_val <= 7 else "hit"
            if pv == 6: return "split" if dealer_val <= 6 else "hit"
        
        if soft:
            if total >= 19: return "stand"
            if total == 18:
                if dealer_val <= 6 and can_double: return "double"
                if dealer_val <= 8: return "stand"
                return "hit"
            if total == 17:
                return "double" if dealer_val in (3,4,5,6) and can_double else "hit"
            if total in (15, 16):
                return "double" if dealer_val in (4,5,6) and can_double else "hit"
            if total in (13, 14):
                return "double" if dealer_val in (5,6) and can_double else "hit"
            return "hit"
        
        if total >= 17: return "stand"
        if total >= 13: return "stand" if dealer_val <= 6 else "hit"
        if total == 12: return "stand" if dealer_val in (4,5,6) else "hit"
        if total == 11: return "double" if can_double else "hit"
        if total == 10: return "double" if can_double and dealer_val <= 9 else "hit"
        if total == 9: return "double" if can_double and dealer_val in (3,4,5,6) else "hit"
        return "hit"


class AggressiveStrategy(Strategy):
    """High-risk, high-reward strategy"""
    @staticmethod
    def decide(hand: Hand, dealer_upcard_rank: str, can_double: bool, can_split: bool, config: Dict) -> str:
        total = hand.value()
        dealer_val = Card(dealer_upcard_rank, '♠').value(config.get('ace_high', True))
        
        if can_split and hand.is_pair():
            pv = hand.cards[0].value(config.get('ace_high', True))
            if pv != 10:
                return "split"
        
        if can_double and total in (9, 10, 11):
            return "double"
        
        if can_double and hand.is_soft() and total in (16, 17, 18):
            return "double"
        
        if total >= 17:
            return "stand"
        
        return "hit"


class MimicDealerStrategy(Strategy):
    """Copy dealer's rules exactly"""
    @staticmethod
    def decide(hand: Hand, dealer_upcard_rank: str, can_double: bool, can_split: bool, config: Dict) -> str:
        total = hand.value()
        return "stand" if total >= 17 else "hit"


class GutFeelStrategy(Strategy):
    """Typical uninformed player"""
    @staticmethod
    def decide(hand: Hand, dealer_upcard_rank: str, can_double: bool, can_split: bool, config: Dict) -> str:
        total = hand.value()
        
        if can_double and total in (10, 11):
            return "double"
        
        if total >= 16:
            return "stand"
        
        return "hit"


# Strategy registry
STRATEGIES = {
    "never_bust": NeverBustStrategy,
    "safe": SafeStrategy,
    "basic": BasicStrategy,
    "aggressive": AggressiveStrategy,
    "mimic_dealer": MimicDealerStrategy,
    "gut_feel": GutFeelStrategy,
    "card_counter": BasicStrategy,  # Uses basic strategy + bet scaling
    "martingale": BasicStrategy,     # Uses basic strategy + martingale betting
}

STRATEGY_NAMES = {
    "never_bust": "Never Bust",
    "safe": "Safe Player",
    "basic": "Basic Strategy",
    "aggressive": "Aggressive",
    "mimic_dealer": "Mimic Dealer",
    "gut_feel": "Gut Feel",
    "card_counter": "Card Counter",
    "martingale": "Martingale",
}


class Player:
    """Represents a player at the table"""
    def __init__(self, name: str, strategy_key: str, config: Dict):
        self.name = name
        self.strategy_key = strategy_key
        self.strategy = STRATEGIES[strategy_key]
        self.config = config
        self.martingale_bet = 1
        self.martingale_max_bet = 16
    
    def bet_size(self, shoe: Shoe) -> int:
        """Calculate bet size"""
        if self.strategy_key == "card_counter":
            tc = shoe.true_count()
            if tc >= 4: return 5
            elif tc >= 2: return 3
            else: return 1
        elif self.strategy_key == "martingale":
            return self.martingale_bet
        return 1
    
    def update_after_round(self, net_payout: float):
        """Update state after round (for martingale)"""
        if self.strategy_key == "martingale":
            if net_payout < 0:
                self.martingale_bet = min(self.martingale_bet * 2, self.martingale_max_bet)
            else:
                self.martingale_bet = 1
    
    def play_hand(self, hand: Hand, dealer_upcard: Card, shoe: Shoe) -> List[Dict]:
        """Play a hand"""
        return self._play(hand, dealer_upcard, shoe, is_split=False)
    
    def _play(self, hand: Hand, dealer_upcard: Card, shoe: Shoe, is_split: bool) -> List[Dict]:
        """Internal hand playing logic"""
        can_double = self.config.get('allow_double_down', True) and len(hand.cards) == 2
        can_split = self.config.get('allow_splits', True) and not is_split and hand.is_pair()
        
        if hand.is_blackjack() and not is_split:
            return [{"cards": hand, "doubled": False, "split_hand": is_split}]
        
        finished = []
        
        while True:
            action = self.strategy.decide(hand, dealer_upcard.rank, can_double, can_split, self.config)
            
            if action == "stand":
                break
            elif action == "hit":
                hand.cards.append(shoe.draw())
                can_double = False
                can_split = False
                if hand.value() >= 21:
                    break
            elif action == "double":
                hand.cards.append(shoe.draw())
                return [{"cards": hand, "doubled": True, "split_hand": is_split}]
            elif action == "split":
                hand_a = Hand([hand.cards[0], shoe.draw()], self.config.get('ace_high', True))
                hand_b = Hand([hand.cards[1], shoe.draw()], self.config.get('ace_high', True))
                finished += self._play(hand_a, dealer_upcard, shoe, is_split=True)
                finished += self._play(hand_b, dealer_upcard, shoe, is_split=True)
                return finished
        
        finished.append({"cards": hand, "doubled": False, "split_hand": is_split})
        return finished


class Dealer:
    """The dealer"""
    def __init__(self, config: Dict):
        self.config = config
    
    def play(self, hand: Hand, shoe: Shoe) -> Hand:
        """Dealer plays their hand"""
        while True:
            val = hand.value()
            soft = hand.is_soft()
            if val > 17:
                break
            if val == 17 and (not soft or self.config.get('dealer_stands_soft', True)):
                break
            hand.cards.append(shoe.draw())
        return hand


def run_simulation(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the blackjack simulation with the given configuration
    
    Args:
        config: Dictionary with simulation parameters
        
    Returns:
        Dictionary with simulation results
    """
    start_time = time.time()
    
    # Extract config
    num_games = config.get('num_games', 10000)
    num_decks = config.get('num_decks', 6)
    blackjack_payout = config.get('blackjack_payout', 1.5)
    dealer_stands_soft = config.get('dealer_stands_soft', True)
    allow_splits = config.get('allow_splits', True)
    allow_double_down = config.get('allow_double_down', True)
    ace_high = config.get('ace_high', True)
    player_strategies = config.get('players', list(STRATEGIES.keys()))
    
    # Initialize game components
    shoe = Shoe(num_decks)
    dealer = Dealer(config)
    players = [Player(STRATEGY_NAMES[s], s, config) for s in player_strategies if s in STRATEGIES]
    
    # Statistics tracking
    player_names = [p.name for p in players]
    outcome_counts = {n: defaultdict(int) for n in player_names}
    payout_totals = defaultdict(float)
    total_bets = defaultdict(float)
    dealer_bj_count = 0
    dealer_bust_count = 0
    total_hands = 0
    
    # Run simulation
    for _ in range(num_games):
        # Deal initial hands
        player_hands = [shoe.deal_hand(ace_high) for _ in players]
        dealer_hand = shoe.deal_hand(ace_high)
        dealer_upcard = dealer_hand.cards[0]
        dealer_bj = dealer_hand.is_blackjack()
        
        # Get bet sizes
        bet_sizes = [p.bet_size(shoe) for p in players]
        
        # Players play
        all_hands = []
        for i, player in enumerate(players):
            hands = player.play_hand(player_hands[i], dealer_upcard, shoe)
            all_hands.append((player, hands))
        
        # Dealer plays if no blackjack
        if not dealer_bj:
            dealer_hand = dealer.play(dealer_hand, shoe)
        
        dealer_val = dealer_hand.value()
        dealer_busted = dealer_val > 21
        
        if dealer_bj:
            dealer_bj_count += 1
        if dealer_busted:
            dealer_bust_count += 1
        
        # Resolve hands
        for i, (player, hands) in enumerate(all_hands):
            bet_mult_base = bet_sizes[i]
            net_payout = 0.0
            bets_round = 0.0
            
            for hand_dict in hands:
                hand = hand_dict["cards"]
                doubled = hand_dict["doubled"]
                player_bj = hand.is_blackjack() and not hand_dict["split_hand"]
                busted = hand.value() > 21
                pval = hand.value()
                bet_mult = bet_mult_base * (2 if doubled else 1)
                
                total_hands += 1
                
                if player_bj and dealer_bj:
                    outcome, payout = "push", 0.0
                elif player_bj:
                    outcome, payout = "blackjack", blackjack_payout * bet_mult
                elif dealer_bj:
                    outcome, payout = "loss", -1.0 * bet_mult
                elif busted:
                    outcome, payout = "bust", -1.0 * bet_mult
                elif dealer_busted:
                    outcome, payout = "win", 1.0 * bet_mult
                elif pval > dealer_val:
                    outcome, payout = "win", 1.0 * bet_mult
                elif pval == dealer_val:
                    outcome, payout = "push", 0.0
                else:
                    outcome, payout = "loss", -1.0 * bet_mult
                
                outcome_counts[player.name][outcome] += 1
                net_payout += payout
                bets_round += bet_mult
            
            payout_totals[player.name] += net_payout
            total_bets[player.name] += bets_round
            player.update_after_round(net_payout)
    
    # Calculate statistics
    player_stats = []
    for player in players:
        name = player.name
        strategy = player.strategy_key
        
        wins = outcome_counts[name]["win"] + outcome_counts[name]["dealer_bust"]
        losses = outcome_counts[name]["loss"] + outcome_counts[name]["bust"]
        pushes = outcome_counts[name]["push"]
        blackjacks = outcome_counts[name]["blackjack"]
        busts = outcome_counts[name]["bust"]
        
        games_played = wins + losses + pushes
        win_rate = wins / games_played if games_played > 0 else 0
        
        total_wagered = total_bets[name]
        total_won = payout_totals[name] + total_wagered
        net_profit = payout_totals[name]
        avg_payout = net_profit / num_games if num_games > 0 else 0
        roi = (net_profit / total_wagered * 100) if total_wagered > 0 else 0
        
        player_stats.append({
            "name": name,
            "strategy": strategy,
            "games_played": games_played,
            "wins": wins,
            "losses": losses,
            "pushes": pushes,
            "blackjacks": blackjacks,
            "busts": busts,
            "win_rate": round(win_rate, 4),
            "average_payout": round(avg_payout, 2),
            "total_wagered": round(total_wagered, 2),
            "total_won": round(total_won, 2),
            "net_profit": round(net_profit, 2),
            "roi": round(roi, 2),
        })
    
    execution_time = time.time() - start_time
    dealer_bust_rate = dealer_bust_count / num_games if num_games > 0 else 0
    
    return {
        "player_stats": player_stats,
        "total_games": num_games,
        "total_hands": total_hands,
        "dealer_busts": dealer_bust_count,
        "dealer_bust_rate": round(dealer_bust_rate, 4),
        "execution_time": round(execution_time, 2),
    }
