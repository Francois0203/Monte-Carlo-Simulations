import random
import statistics
from collections import defaultdict


# ─────────────────────────────────────────────────────────────────
#  SETTINGS — change these to customise your simulation
# ─────────────────────────────────────────────────────────────────

NUM_GAMES          = 10_000
NUM_DECKS          = 6        # cards in the shoe (6 is standard casino)
BLACKJACK_PAYOUT   = 1.5      # 3:2 is the standard casino payout
DEALER_STANDS_SOFT = True     # True = dealer must stand on soft 17 (casino standard)
ALLOW_SPLITS       = True     # players can split a matching pair
ALLOW_DOUBLE_DOWN  = True     # players can double their bet on the first two cards

# Ace value rule:
#   True  — Ace counts as 1 OR 11, whichever helps (standard blackjack)
#   False — Ace always counts as 1 only (makes the game much harder)
ACE_HIGH = True

# The eight players sitting at the table — one of each strategy style.
# Each entry is (display name, strategy).
# Strategy options:
#   "never_bust"   — stand on any 12+, never risk busting
#   "safe"         — stand on 13+, minimal doubles/splits
#   "basic"        — mathematically optimal play
#   "aggressive"   — hit until 17+, split and double liberally
#   "mimic_dealer" — copy the dealer's fixed hit/stand rules exactly
#   "gut_feel"     — stand on 16+, double only on 10/11
#   "card_counter" — basic strategy + raises bets when running count is high
#   "martingale"   — basic strategy decisions + doubles bet after each loss
PLAYERS = [
    ("Never Bust",     "never_bust"),
    ("Safe Player",    "safe"),
    ("Basic Strategy", "basic"),
    ("Aggressive",     "aggressive"),
    ("Mimic Dealer",   "mimic_dealer"),
    ("Gut Feel",       "gut_feel"),
    ("Card Counter",   "card_counter"),
    ("Martingale",     "martingale"),
]


# ─────────────────────────────────────────────────────────────────
#  CARD & HAND HELPERS
# ─────────────────────────────────────────────────────────────────

RANKS = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
SUITS = ['♠','♥','♦','♣']

def card_value(rank):
    """Face cards = 10. Ace = 11 to start (hand_value will flip it if needed)."""
    if rank in ('J', 'Q', 'K'): return 10
    if rank == 'A':              return 11 if ACE_HIGH else 1
    return int(rank)

def hand_value(cards):
    """
    Returns the best possible value for a hand without going over 21.
    If an Ace would cause a bust at 11, it gets flipped down to 1.
    """
    total = sum(card_value(r) for r, s in cards)
    if ACE_HIGH:
        aces = sum(1 for r, s in cards if r == 'A')
        while total > 21 and aces:
            total -= 10
            aces  -= 1
    return total

def is_soft(cards):
    """
    A 'soft' hand has an Ace still counted as 11.
    e.g. Ace + 6 = soft 17. Ace + 6 + 9 = hard 16 (Ace flipped to 1).
    Always False when ACE_HIGH is off.
    """
    if not ACE_HIGH:
        return False
    total = sum(card_value(r) for r, s in cards)
    aces  = sum(1 for r, s in cards if r == 'A')
    while total > 21 and aces:
        total -= 10
        aces  -= 1
    return aces > 0 and total <= 21

def is_blackjack(cards):
    """Natural blackjack: exactly two cards that add up to 21."""
    return len(cards) == 2 and hand_value(cards) == 21

def is_pair(cards):
    """True if the opening two cards have the same point value."""
    return len(cards) == 2 and card_value(cards[0][0]) == card_value(cards[1][0])


# ─────────────────────────────────────────────────────────────────
#  SHOE (the deck)
#  A casino uses multiple decks shuffled into a "shoe" to make
#  card counting harder. We reshuffle when ~25% of cards remain.
# ─────────────────────────────────────────────────────────────────

class Shoe:
    def __init__(self):
        self.running_count = 0
        self.reshuffle()

    def reshuffle(self):
        self.cards = [(rank, suit)
                      for _ in range(NUM_DECKS)
                      for suit in SUITS
                      for rank in RANKS]
        random.shuffle(self.cards)
        self.reshuffle_point = len(self.cards) // 4
        self.running_count   = 0  # count resets on reshuffle

    def draw(self):
        if len(self.cards) <= self.reshuffle_point:
            self.reshuffle()
        card  = self.cards.pop()
        rank  = card[0]
        # Hi-Lo card counting: low cards (2-6) are +1, high cards (10+) are -1
        val   = card_value(rank)
        if 2 <= val <= 6:
            self.running_count += 1
        elif val >= 10:
            self.running_count -= 1
        return card

    def true_count(self):
        """True count = running count / decks remaining (used by card counter)."""
        decks_remaining = max(0.5, len(self.cards) / 52)
        return self.running_count / decks_remaining

    def deal_hand(self):
        return [self.draw(), self.draw()]


# ─────────────────────────────────────────────────────────────────
#  THE EIGHT STRATEGIES
# ─────────────────────────────────────────────────────────────────

def never_bust_strategy(cards, dealer_upcard_rank, can_double, can_split):
    """
    Stand on any 12 or higher — never risk busting.
    Extremely passive: often surrenders winnable hands.
    """
    total = hand_value(cards)
    if total >= 12:
        return "stand"
    return "hit"


def safe_strategy(cards, dealer_upcard_rank, can_double, can_split):
    """
    Stand early, minimise risk. The safe player's logic:
    - Never splits except Aces (too risky to put more money in)
    - Only doubles on a very strong 11 vs a weak dealer
    - Stands on anything 13 or above, no matter what the dealer has
    """
    total      = hand_value(cards)
    dealer_val = card_value(dealer_upcard_rank)

    if can_split and is_pair(cards):
        if card_value(cards[0][0]) == 11:
            return "split"

    if can_double and total == 11 and dealer_val <= 6:
        return "double"

    if total >= 13:
        return "stand"

    return "hit"


def basic_strategy(cards, dealer_upcard_rank, can_double, can_split):
    """
    The mathematically correct play for every situation.
    This is what professional players memorise and casinos try to
    discourage. Over millions of hands it minimises the house edge.
    """
    total      = hand_value(cards)
    soft       = is_soft(cards)
    dealer_val = card_value(dealer_upcard_rank)
    pair       = is_pair(cards) and can_split

    if pair:
        pv = card_value(cards[0][0])
        if pv == 11:  return "split"
        if pv == 8:   return "split"
        if pv == 10:  return "stand"
        if pv == 5:   return "double" if can_double and dealer_val <= 9 else "hit"
        if pv == 4:   return "split" if dealer_val in (5, 6) else "hit"
        if pv == 9:   return "stand" if dealer_val in (7, 10, 11) else "split"
        if pv in (2, 3, 7): return "split" if dealer_val <= 7 else "hit"
        if pv == 6:   return "split" if dealer_val <= 6 else "hit"

    if soft:
        if total >= 19: return "stand"
        if total == 18:
            if dealer_val <= 6 and can_double: return "double"
            if dealer_val <= 8:                return "stand"
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
    if total == 9:  return "double" if can_double and dealer_val in (3,4,5,6) else "hit"
    return "hit"


def aggressive_strategy(cards, dealer_upcard_rank, can_double, can_split):
    """
    High-risk, high-reward. The aggressive player:
    - Splits almost every pair to get more money on the table
    - Doubles down on a wider range of hands
    - Never stands below 17 — always chases a better hand
    """
    total      = hand_value(cards)
    dealer_val = card_value(dealer_upcard_rank)

    if can_split and is_pair(cards):
        pv = card_value(cards[0][0])
        if pv != 10:
            return "split"

    if can_double and total in (9, 10, 11):
        return "double"

    if can_double and is_soft(cards) and total in (16, 17, 18):
        return "double"

    if total >= 17:
        return "stand"

    return "hit"


def mimic_dealer_strategy(cards, dealer_upcard_rank, can_double, can_split):
    """
    Copies the dealer exactly: hit until 17+, then stand.
    No doubling, no splitting. Ignores the dealer's upcard.
    Interesting because it shows why the house edge exists even
    when players use the same rules — players bust first.
    """
    total = hand_value(cards)
    if total >= 17:
        return "stand"
    return "hit"


def gut_feel_strategy(cards, dealer_upcard_rank, can_double, can_split):
    """
    A typical uninformed player: stands on 16+, doubles only on
    10 or 11, never splits. Better than never-bust but well below basic.
    """
    total      = hand_value(cards)
    dealer_val = card_value(dealer_upcard_rank)

    if can_double and total in (10, 11):
        return "double"

    if total >= 16:
        return "stand"

    return "hit"


def card_counter_strategy(cards, dealer_upcard_rank, can_double, can_split):
    """
    Uses basic strategy for hand decisions (identical to basic_strategy).
    The difference is handled in the Player class: bets are scaled up
    when the true count is high (lots of high cards remaining in the shoe).
    This is tracked separately in the simulation stats.
    """
    return basic_strategy(cards, dealer_upcard_rank, can_double, can_split)


def martingale_strategy(cards, dealer_upcard_rank, can_double, can_split):
    """
    Uses basic strategy for hand decisions (identical to basic_strategy).
    The martingale bet-sizing (double bet after each loss, reset after win)
    is tracked separately in the Player class.
    """
    return basic_strategy(cards, dealer_upcard_rank, can_double, can_split)


# Map strategy name → function
STRATEGY_MAP = {
    "never_bust":   never_bust_strategy,
    "safe":         safe_strategy,
    "basic":        basic_strategy,
    "aggressive":   aggressive_strategy,
    "mimic_dealer": mimic_dealer_strategy,
    "gut_feel":     gut_feel_strategy,
    "card_counter": card_counter_strategy,
    "martingale":   martingale_strategy,
}

# Max bet multiplier for martingale (caps the runaway doubling)
MARTINGALE_MAX_BET = 16


# ─────────────────────────────────────────────────────────────────
#  PLAYER
# ─────────────────────────────────────────────────────────────────

class Player:
    def __init__(self, name, strategy_name):
        self.name          = name
        self.strategy_name = strategy_name
        self.strategy_fn   = STRATEGY_MAP[strategy_name]

        # Martingale state
        self.martingale_bet = 1   # current bet multiplier (doubles after a loss)

        # Card counter state (true count is read from the shoe)
        self.count_bet_multiplier = 1

    def bet_size(self, shoe):
        """
        Returns the bet multiplier for this round.
        - Normal strategies: always 1 unit.
        - Card counter: 1 unit normally, 3 units when true count >= 2,
          5 units when true count >= 4 (high count = player advantage).
        - Martingale: doubles after each loss, capped at MARTINGALE_MAX_BET.
        """
        if self.strategy_name == "card_counter":
            tc = shoe.true_count()
            if tc >= 4:   return 5
            elif tc >= 2: return 3
            else:         return 1
        elif self.strategy_name == "martingale":
            return self.martingale_bet
        return 1

    def update_after_round(self, net_payout_before_bet_scaling):
        """
        Update bet-sizing state after each round.
        Only relevant for martingale.
        """
        if self.strategy_name == "martingale":
            if net_payout_before_bet_scaling < 0:
                # Lost — double the bet next round, up to the cap
                self.martingale_bet = min(self.martingale_bet * 2, MARTINGALE_MAX_BET)
            else:
                # Won or pushed — reset to base bet
                self.martingale_bet = 1

    def play_hand(self, cards, dealer_upcard, shoe):
        return self._play(cards, dealer_upcard, shoe, is_split=False)

    def _play(self, cards, dealer_upcard, shoe, is_split):
        can_double  = ALLOW_DOUBLE_DOWN and len(cards) == 2
        can_split   = ALLOW_SPLITS and not is_split and is_pair(cards)
        dealer_rank = dealer_upcard[0]

        if is_blackjack(cards) and not is_split:
            return [{"cards": cards, "doubled": False, "split_hand": is_split}]

        finished = []

        while True:
            action = self.strategy_fn(cards, dealer_rank, can_double, can_split)

            if action == "stand":
                break

            elif action == "hit":
                cards.append(shoe.draw())
                can_double = False
                can_split  = False
                if hand_value(cards) >= 21:
                    break

            elif action == "double":
                cards.append(shoe.draw())
                return [{"cards": cards, "doubled": True, "split_hand": is_split}]

            elif action == "split":
                hand_a = [cards[0], shoe.draw()]
                hand_b = [cards[1], shoe.draw()]
                finished += self._play(hand_a, dealer_upcard, shoe, is_split=True)
                finished += self._play(hand_b, dealer_upcard, shoe, is_split=True)
                return finished

        finished.append({"cards": cards, "doubled": False, "split_hand": is_split})
        return finished


# ─────────────────────────────────────────────────────────────────
#  DEALER
# ─────────────────────────────────────────────────────────────────

class Dealer:
    def play(self, cards, shoe):
        while True:
            val  = hand_value(cards)
            soft = is_soft(cards)
            if val > 17:  break
            if val == 17 and (not soft or DEALER_STANDS_SOFT): break
            cards.append(shoe.draw())
        return cards


# ─────────────────────────────────────────────────────────────────
#  GAME — one full round at the table
# ─────────────────────────────────────────────────────────────────

class Game:
    def __init__(self):
        self.shoe    = Shoe()
        self.players = [Player(name, strat) for name, strat in PLAYERS]
        self.dealer  = Dealer()

    def play(self):
        player_cards  = [self.shoe.deal_hand() for _ in self.players]
        dealer_cards  = self.shoe.deal_hand()
        dealer_upcard = dealer_cards[0]
        dealer_bj     = is_blackjack(dealer_cards)

        # Capture bet sizes BEFORE hands are played (card counter reads shoe here)
        bet_sizes = [p.bet_size(self.shoe) for p in self.players]

        # Each player acts on their hand(s)
        all_hands = []
        for i, player in enumerate(self.players):
            hands = player.play_hand(player_cards[i], dealer_upcard, self.shoe)
            all_hands.append((player.name, player.strategy_name, hands))

        if not dealer_bj:
            dealer_cards = self.dealer.play(dealer_cards, self.shoe)

        dealer_val    = hand_value(dealer_cards)
        dealer_busted = dealer_val > 21

        player_results = []
        for i, (player_name, strategy_name, hands) in enumerate(all_hands):
            bet_mult_base = bet_sizes[i]
            hand_results  = []

            for hand in hands:
                cards     = hand["cards"]
                doubled   = hand["doubled"]
                player_bj = is_blackjack(cards) and not hand["split_hand"]
                busted    = hand_value(cards) > 21
                pval      = hand_value(cards)
                bet_mult  = bet_mult_base * (2 if doubled else 1)

                if   player_bj and dealer_bj: outcome, payout = "push",        0.0
                elif player_bj:               outcome, payout = "blackjack",   BLACKJACK_PAYOUT * bet_mult
                elif dealer_bj:               outcome, payout = "loss",       -1.0 * bet_mult
                elif busted:                  outcome, payout = "bust",        -1.0 * bet_mult
                elif dealer_busted:           outcome, payout = "dealer_bust",  1.0 * bet_mult
                elif pval > dealer_val:       outcome, payout = "win",          1.0 * bet_mult
                elif pval == dealer_val:      outcome, payout = "push",         0.0
                else:                         outcome, payout = "loss",        -1.0 * bet_mult

                hand_results.append({
                    "outcome":   outcome,
                    "payout":    payout,
                    "final_val": pval,
                    "doubled":   doubled,
                    "split":     hand["split_hand"],
                    "bet_mult":  bet_mult,
                })

            # Let player update martingale state
            net_raw = sum(h["payout"] for h in hand_results)
            self.players[i].update_after_round(net_raw)

            player_results.append({
                "player":   player_name,
                "strategy": strategy_name,
                "hands":    hand_results,
            })

        return {
            "player_results": player_results,
            "dealer_bj":      dealer_bj,
            "dealer_busted":  dealer_busted,
            "dealer_final":   dealer_val,
        }


# ─────────────────────────────────────────────────────────────────
#  SIMULATION — plays NUM_GAMES rounds and tracks everything
# ─────────────────────────────────────────────────────────────────

class Simulation:
    def __init__(self):
        self.game = Game()

        player_names = [name for name, _ in PLAYERS]

        self.outcome_counts  = {n: defaultdict(int)   for n in player_names}
        self.payout_totals   = defaultdict(float)
        self.payout_per_game = defaultdict(list)
        self.hand_values     = defaultdict(list)
        self.doubles_taken   = defaultdict(int)
        self.splits_taken    = defaultdict(int)
        self.total_bets      = defaultdict(float)

        self.current_win_streak  = defaultdict(int)
        self.current_loss_streak = defaultdict(int)
        self.max_win_streak      = defaultdict(int)
        self.max_loss_streak     = defaultdict(int)

        self.dealer_final_vals = []
        self.dealer_bj_count   = 0
        self.dealer_bust_count = 0
        self.total_hands       = 0

    def run(self):
        for _ in range(NUM_GAMES):
            result = self.game.play()
            self._record(result)

    def _record(self, result):
        self.dealer_final_vals.append(result["dealer_final"])
        if result["dealer_bj"]:    self.dealer_bj_count   += 1
        if result["dealer_busted"]: self.dealer_bust_count += 1

        for pr in result["player_results"]:
            name       = pr["player"]
            net_payout = 0.0
            bets_round = 0.0

            for hand in pr["hands"]:
                self.total_hands += 1
                self.outcome_counts[name][hand["outcome"]] += 1
                self.hand_values[name].append(hand["final_val"])

                net_payout += hand["payout"]
                bets_round += hand["bet_mult"]

                if hand["doubled"]: self.doubles_taken[name] += 1
                if hand["split"]:   self.splits_taken[name]  += 1

            self.payout_totals[name]     += net_payout
            self.total_bets[name]        += bets_round
            self.payout_per_game[name].append(net_payout)

            if net_payout > 0:
                self.current_win_streak[name]  += 1
                self.current_loss_streak[name]  = 0
            elif net_payout < 0:
                self.current_loss_streak[name] += 1
                self.current_win_streak[name]   = 0

            self.max_win_streak[name]  = max(self.max_win_streak[name],
                                             self.current_win_streak[name])
            self.max_loss_streak[name] = max(self.max_loss_streak[name],
                                             self.current_loss_streak[name])

    # ─────────────────────────────────────────────────────────────
    #  REPORT
    # ─────────────────────────────────────────────────────────────

    def report(self):
        W    = 68
        sep  = "─" * W
        sep2 = "━" * W

        def pct(n, d):
            return f"{n / d * 100:.1f}%" if d else "n/a"

        # ── Header ───────────────────────────────────────────────
        print(f"\n{'═' * W}")
        print(f"  ♠♥  BLACKJACK SIMULATION REPORT  ♦♣")
        print(f"{'═' * W}")
        print(f"  Games simulated  : {NUM_GAMES:,}")
        print(f"  Decks in shoe    : {NUM_DECKS}  (reshuffled at 25% remaining)")
        print(f"  Blackjack payout : {BLACKJACK_PAYOUT:.1f}:1  (3:2 standard)")
        print(f"  Dealer on soft 17: {'stands' if DEALER_STANDS_SOFT else 'hits'}")
        print(f"  Splitting        : {'allowed' if ALLOW_SPLITS else 'not allowed'}")
        print(f"  Doubling down    : {'allowed' if ALLOW_DOUBLE_DOWN else 'not allowed'}")
        print(f"  Ace counts as    : {'1 or 11 (standard)' if ACE_HIGH else 'always 1'}")
        print(f"  Total hands dealt: {self.total_hands:,}  (extra hands from splits)")

        # ── Dealer ───────────────────────────────────────────────
        print(f"\n{sep}")
        print("  THE DEALER")
        print(sep)
        print(f"  The dealer follows fixed rules — no choices, no strategy.")
        print(f"  They must keep hitting until they reach 17 or higher.")
        print()
        print(f"  Blackjacks  : {self.dealer_bj_count:,}  ({pct(self.dealer_bj_count, NUM_GAMES)})")
        print(f"  Busts (>21) : {self.dealer_bust_count:,}  ({pct(self.dealer_bust_count, NUM_GAMES)})")
        print(f"  Avg hand    : {statistics.mean(self.dealer_final_vals):.2f}")
        print()
        print(f"  How often the dealer finishes on each value:")
        for val in range(17, 22):
            count = sum(1 for v in self.dealer_final_vals if v == val)
            bar   = "█" * int(count / NUM_GAMES * 100)
            print(f"    {val}  {bar:<20} {count:,}  ({pct(count, NUM_GAMES)})")
        bust_count = sum(1 for v in self.dealer_final_vals if v > 21)
        bar = "█" * int(bust_count / NUM_GAMES * 100)
        print(f"   22+  {bar:<20} {bust_count:,}  ({pct(bust_count, NUM_GAMES)})  ← bust")

        # ── Strategy descriptions ─────────────────────────────────
        STRATEGY_DESCRIPTIONS = {
            "never_bust":   ("Stands on 12+. Never risks busting — often leaves weak hands.",
                             "Most passive strategy possible. Surrenders many winnable hands.",
                             None),
            "safe":         ("Stands on 13+. Only doubles 11 vs weak dealer. Only splits Aces.",
                             "Prioritises not busting over winning big.",
                             None),
            "basic":        ("Plays the mathematically optimal decision every time.",
                             "Accounts for the dealer's upcard in every choice.",
                             None),
            "aggressive":   ("Hits until 17+. Splits almost all pairs. Doubles on 9/10/11.",
                             "Accepts more busts in exchange for bigger potential wins.",
                             None),
            "mimic_dealer": ("Copies the dealer: hits until 17+, stands on 17+. No doubles/splits.",
                             "Reveals why the house edge exists — players bust first, dealer wins ties.",
                             None),
            "gut_feel":     ("Stands on 16+. Doubles only on 10/11. Never splits.",
                             "Typical uninformed player — better than never-bust, worse than basic.",
                             None),
            "card_counter": ("Basic strategy decisions with scaled bets based on the true count.",
                             "Bets 1 unit normally, 3 units at TC≥2, 5 units at TC≥4.",
                             "Note: bet scaling means house edge here reflects true profitability."),
            "martingale":   ("Basic strategy decisions with progressive bet sizing.",
                             "Doubles bet after each loss (capped at 16 units), resets after a win.",
                             "Note: high bets mean net units aren't directly comparable to flat bettors."),
        }

        # ── Per-player sections ───────────────────────────────────
        for name, strategy_name in PLAYERS:
            counts  = self.outcome_counts[name]
            payouts = self.payout_per_game[name]
            rounds  = len(payouts)

            wins   = counts["win"] + counts["blackjack"] + counts["dealer_bust"]
            losses = counts["loss"] + counts["bust"]
            pushes = counts["push"]
            total  = wins + losses + pushes

            net        = self.payout_totals[name]
            house_edge = -net / self.total_bets[name] * 100 if self.total_bets[name] else 0
            avg_payout = statistics.mean(payouts)

            edge_label = "house profits" if house_edge > 0 else "player profits"

            desc1, desc2, note = STRATEGY_DESCRIPTIONS.get(strategy_name, ("","",None))

            print(f"\n{sep2}")
            print(f"  {name.upper()}  [{strategy_name.upper()} STRATEGY]")
            print(sep2)
            print(f"  {desc1}")
            print(f"  {desc2}")
            if note:
                print(f"  ⚑  {note}")
            print()

            print(f"  RESULTS over {rounds:,} rounds:")
            print(f"  {'Wins':<14} {wins:>6,}  ({pct(wins, total)})  ← beat the dealer")
            print(f"    {'Blackjacks':<12} {counts['blackjack']:>6,}  ({pct(counts['blackjack'], total)})  ← natural 21, pays {BLACKJACK_PAYOUT:.1f}x")
            print(f"    {'Regular wins':<12} {counts['win']:>6,}  ({pct(counts['win'], total)})  ← higher hand than dealer")
            print(f"    {'Dealer busted':<12} {counts['dealer_bust']:>6,}  ({pct(counts['dealer_bust'], total)})  ← dealer went over 21")
            print(f"  {'Losses':<14} {losses:>6,}  ({pct(losses, total)})")
            print(f"    {'Regular losses':<12} {counts['loss']:>6,}  ({pct(counts['loss'], total)})  ← lower hand than dealer")
            print(f"    {'Busted':<12} {counts['bust']:>6,}  ({pct(counts['bust'], total)})  ← went over 21")
            print(f"  {'Pushes':<14} {pushes:>6,}  ({pct(pushes, total)})  ← tied with dealer, bet returned")
            print()

            print(f"  MONEY  (1 unit = 1 flat bet; card counter & martingale scale bets):")
            print(f"  Net profit/loss    : {net:>+8.1f} units over {NUM_GAMES:,} games")
            print(f"  Average per round  : {avg_payout:>+8.4f} units")
            print(f"  House edge         : {house_edge:>+7.2f}%  ({edge_label})")
            print(f"  → For every 100 units bet, this player "
                  f"{'loses' if house_edge > 0 else 'wins'} "
                  f"~{abs(house_edge):.1f} units on average.")
            print()

            bj_per_round = counts['blackjack'] / rounds if rounds else 0
            print(f"  HAND STATS:")
            print(f"  Avg final hand value : {statistics.mean(self.hand_values[name]):.2f}")
            print(f"  Bust rate            : {pct(counts['bust'], total)}")
            print(f"  Blackjack rate       : {pct(counts['blackjack'], rounds)}  "
                  f"(about 1 in {int(1/bj_per_round) if bj_per_round else '?'} rounds)")
            print(f"  Doubles taken        : {self.doubles_taken[name]:,}  "
                  f"({self.doubles_taken[name] / rounds:.2f} per round)")
            print(f"  Splits taken         : {self.splits_taken[name]:,}  "
                  f"({self.splits_taken[name] / rounds:.2f} per round)")
            print()

            win_rounds  = sum(1 for p in payouts if p > 0)
            loss_rounds = sum(1 for p in payouts if p < 0)
            push_rounds = sum(1 for p in payouts if p == 0)
            print(f"  STREAKS & VARIANCE:")
            print(f"  Profitable rounds  : {win_rounds:,}  ({pct(win_rounds, rounds)})")
            print(f"  Losing rounds      : {loss_rounds:,}  ({pct(loss_rounds, rounds)})")
            print(f"  Break-even rounds  : {push_rounds:,}  ({pct(push_rounds, rounds)})")
            print(f"  Longest win streak : {self.max_win_streak[name]} rounds in a row")
            print(f"  Longest loss streak: {self.max_loss_streak[name]} rounds in a row")

        # ── Head-to-head comparison ───────────────────────────────
        print(f"\n{'═' * W}")
        print("  HEAD-TO-HEAD COMPARISON")
        print(f"{'═' * W}")
        print(f"  {'Player':<20} {'Strategy':<14} {'Win%':>6}  {'Bust%':>6}  "
              f"{'Avg hand':>8}  {'House edge':>10}  {'Net':>8}")
        print(f"  {sep}")

        for name, strategy_name in PLAYERS:
            counts = self.outcome_counts[name]
            wins   = counts["win"] + counts["blackjack"] + counts["dealer_bust"]
            total  = wins + counts["loss"] + counts["bust"] + counts["push"]
            edge   = (-self.payout_totals[name] / self.total_bets[name] * 100
                      if self.total_bets[name] else 0)
            avg_hv = statistics.mean(self.hand_values[name])
            net    = self.payout_totals[name]

            print(f"  {name:<20} {strategy_name:<14} "
                  f"{pct(wins, total):>6}  "
                  f"{pct(counts['bust'], total):>6}  "
                  f"{avg_hv:>8.2f}  "
                  f"{edge:>+10.2f}%  "
                  f"{net:>+8.1f}")

        print()
        print("  What this tells us:")

        edges = {n: (-self.payout_totals[n] / self.total_bets[n] * 100
                     if self.total_bets[n] else 0)
                 for n, _ in PLAYERS}
        best  = min(edges, key=edges.get)
        worst = max(edges, key=edges.get)

        print(f"  • {best} had the lowest house edge — best outcome for the player.")
        print(f"  • {worst} had the highest house edge — most profitable for the casino.")

        best_bust  = min(PLAYERS, key=lambda p: self.outcome_counts[p[0]]["bust"])
        worst_bust = max(PLAYERS, key=lambda p: self.outcome_counts[p[0]]["bust"])
        print(f"  • {best_bust[0]} busted least often.")
        print(f"  • {worst_bust[0]} busted most often.")

        print(f"\n  Strategy ranking by house edge (lower = better for the player):")
        ranked = sorted(PLAYERS, key=lambda p: edges[p[0]])
        for rank, (name, strat) in enumerate(ranked, 1):
            marker = " ← best" if rank == 1 else (" ← worst" if rank == len(ranked) else "")
            print(f"    {rank}. {name:<20} {edges[name]:>+7.2f}%{marker}")

        print(f"\n{'═' * W}\n")


# ─────────────────────────────────────────────────────────────────
#  RUN IT
# ─────────────────────────────────────────────────────────────────

sim = Simulation()
sim.run()
sim.report()