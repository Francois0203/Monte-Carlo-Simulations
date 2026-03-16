import random
import statistics
from collections import defaultdict
from itertools import combinations


# ─────────────────────────────────────────────────────────────────
#  SETTINGS — change these to customise your simulation
# ─────────────────────────────────────────────────────────────────

NUM_HANDS          = 10_000   # number of hands to simulate
NUM_PLAYERS        = 6        # players at the table (2–9)
SMALL_BLIND        = 1        # small blind in chips
BIG_BLIND          = 2        # big blind in chips (standard = 2× small blind)
STARTING_STACK     = 200      # starting chip stack for every player (100 BB is standard)

# When a player runs out of chips they are eliminated.
# Set to True to rebuy everyone back to STARTING_STACK when busted.
ALLOW_REBUYS       = True

# Players list — each entry is (display name, strategy).
# Strategy options:
#   "calling_station" — calls almost everything, rarely raises, never folds pre-flop
#   "tight_passive"   — only plays strong hands, but just calls instead of raising
#   "tight_aggressive"— TAG: strong hand selection + bets and raises for value
#   "loose_aggressive"— LAG: plays many hands, bluffs often, applies constant pressure
#   "pot_odds_player" — calls/folds based purely on pot odds vs hand equity
#   "bluffer"         — wide range, high bluff frequency, bets big to push others out
#   "position_aware"  — tightens from early position, loosens from late position
#   "gto_balanced"    — approximates game-theory optimal mixed strategy
PLAYERS = [
    ("Calling Station",  "calling_station"),
    ("Tight Passive",    "tight_passive"),
    ("Tight Aggressive", "tight_aggressive"),
    ("Loose Aggressive", "loose_aggressive"),
    ("Pot Odds Player",  "pot_odds_player"),
    ("Bluffer",          "bluffer"),
    ("Position Aware",   "position_aware"),
    ("GTO Balanced",     "gto_balanced"),
]


# ─────────────────────────────────────────────────────────────────
#  CARD CONSTANTS & HELPERS
# ─────────────────────────────────────────────────────────────────

RANKS   = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
SUITS   = ['♠','♥','♦','♣']
RANK_VAL = {r: i for i, r in enumerate(RANKS)}   # '2'→0 … 'A'→12

# Hand rank constants (higher = better)
HIGH_CARD       = 0
ONE_PAIR        = 1
TWO_PAIR        = 2
THREE_OF_A_KIND = 3
STRAIGHT        = 4
FLUSH           = 5
FULL_HOUSE      = 6
FOUR_OF_A_KIND  = 7
STRAIGHT_FLUSH  = 8
ROYAL_FLUSH     = 9

HAND_NAMES = {
    HIGH_CARD: "High card", ONE_PAIR: "One pair", TWO_PAIR: "Two pair",
    THREE_OF_A_KIND: "Three of a kind", STRAIGHT: "Straight", FLUSH: "Flush",
    FULL_HOUSE: "Full house", FOUR_OF_A_KIND: "Four of a kind",
    STRAIGHT_FLUSH: "Straight flush", ROYAL_FLUSH: "Royal flush",
}


def make_deck():
    return [(r, s) for s in SUITS for r in RANKS]


def rank_val(card):
    return RANK_VAL[card[0]]


def evaluate_hand(cards):
    """
    Evaluate the best 5-card hand from up to 7 cards (hole + community).
    Returns (hand_rank, tiebreaker_tuple) — higher is always better.
    The tiebreaker is a tuple of rank values used to break ties within
    the same hand category.
    """
    best = (-1, ())
    for combo in combinations(cards, 5):
        score = score_five(combo)
        if score > best:
            best = score
    return best


def score_five(cards):
    """Score exactly 5 cards. Returns (hand_rank, tiebreaker_tuple)."""
    vals  = sorted([rank_val(c) for c in cards], reverse=True)
    suits = [c[1] for c in cards]
    is_flush    = len(set(suits)) == 1
    is_straight = _is_straight(vals)

    counts = defaultdict(int)
    for v in vals:
        counts[v] += 1
    freq = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
    grouped = [v for v, _ in freq]
    cnt     = [c for _, c in freq]

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


def _is_straight(sorted_vals):
    """True if 5 sorted (desc) values form a straight. Handles A-2-3-4-5 wheel."""
    if sorted_vals[0] - sorted_vals[4] == 4 and len(set(sorted_vals)) == 5:
        return True
    # Wheel: A-2-3-4-5  (Ace counted as low)
    if sorted_vals == [12, 3, 2, 1, 0]:
        return True
    return False


def hand_name(score):
    return HAND_NAMES.get(score[0], "Unknown")


# ─────────────────────────────────────────────────────────────────
#  STARTING HAND CLASSIFICATION
#  Used by strategies to decide how strong hole cards are before
#  any community cards are dealt.
# ─────────────────────────────────────────────────────────────────

def classify_hole_cards(hole):
    """
    Classify a two-card starting hand into a tier.
    Returns one of: "premium", "strong", "speculative", "marginal", "trash"
    """
    r1, r2 = sorted([rank_val(c) for c in hole], reverse=True)
    suited  = hole[0][1] == hole[1][1]
    paired  = r1 == r2

    # Pocket pairs
    if paired:
        if r1 >= 10: return "premium"     # AA, KK, QQ, JJ
        if r1 >= 7:  return "strong"      # TT, 99, 88
        if r1 >= 4:  return "speculative" # 77, 66, 55
        return "marginal"                 # 44, 33, 22

    # Unpaired
    gap = r1 - r2

    if r1 == 12:   # Ace-x
        if r2 >= 10: return "premium"     # AK, AQ, AJ, AT
        if r2 >= 7:  return "strong"      # A9s–A7s
        if suited:   return "speculative" # A6s–A2s
        return "marginal"                 # A6o–A2o

    if r1 >= 10 and r2 >= 9:             # KQ, KJ, QJ, etc.
        return "strong" if not suited or gap <= 1 else "strong"

    if r1 >= 9 and gap <= 1 and suited:  # connectors like 98s, 87s
        return "speculative"

    if r1 >= 9 and gap <= 2:             # one-gap connectors
        return "speculative" if suited else "marginal"

    if r1 >= 7 and gap <= 1 and suited:  # small suited connectors
        return "marginal"

    return "trash"


def hole_card_equity(hole):
    """
    Fast approximate pre-flop equity (0.0–1.0) using a hand strength
    heuristic. Not a full Monte Carlo — just for pot-odds decisions.
    """
    tier = classify_hole_cards(hole)
    base = {"premium": 0.72, "strong": 0.60, "speculative": 0.50,
            "marginal": 0.42, "trash": 0.35}
    suited_bonus = 0.02 if hole[0][1] == hole[1][1] else 0.0
    return base[tier] + suited_bonus


# ─────────────────────────────────────────────────────────────────
#  QUICK MONTE CARLO EQUITY ESTIMATE
#  Used post-flop by the pot_odds_player.
#  Runs N random runouts and returns win probability vs one opponent.
# ─────────────────────────────────────────────────────────────────

def estimate_equity(hole, community, num_opponents=1, simulations=50):
    """
    Fast equity estimate via small Monte Carlo sample (50 runouts).
    Accurate enough for in-hand decisions without slowing the sim.
    """
    used  = set((c[0], c[1]) for c in hole + community)
    deck  = [(r, s) for s in SUITS for r in RANKS if (r, s) not in used]
    cards_needed = 5 - len(community)
    wins = 0
    ran  = 0
    for _ in range(simulations):
        random.shuffle(deck)
        if len(deck) < cards_needed + 2:
            break
        runout    = community + deck[:cards_needed]
        opp_hole  = deck[cards_needed:cards_needed + 2]
        my_score  = evaluate_hand(hole + runout)
        opp_score = evaluate_hand(opp_hole + runout)
        if my_score > opp_score:
            wins += 1
        elif my_score == opp_score:
            wins += 0.5
        ran += 1
    return wins / ran if ran else 0.5


# ─────────────────────────────────────────────────────────────────
#  THE EIGHT STRATEGIES
#
#  Each strategy function receives:
#    hole        — player's two hole cards [(rank, suit), ...]
#    community   — community cards dealt so far (0, 3, 4, or 5 cards)
#    pot         — current pot size in chips
#    to_call     — chips needed to call (0 = player can check)
#    stack       — player's remaining stack
#    position    — 0 = early, 1 = middle, 2 = late, 3 = blinds
#    street      — "preflop", "flop", "turn", "river"
#    num_active  — how many players are still in the hand
#    aggression  — how many raises have happened this street (0, 1, 2 …)
#
#  Returns one of:
#    ("fold",  0)          — fold, losing any chips already in the pot
#    ("check", 0)          — check (only valid when to_call == 0)
#    ("call",  to_call)    — call the current bet
#    ("raise", amount)     — raise by 'amount' chips on top of to_call
#    ("all_in", stack)     — go all-in
# ─────────────────────────────────────────────────────────────────

def calling_station(hole, community, pot, to_call, stack, position,
                    street, num_active, aggression):
    """
    Calls almost everything. Never folds unless holding absolute trash
    pre-flop facing a big raise. Rarely raises. A casino fish.
    """
    tier = classify_hole_cards(hole)

    if street == "preflop":
        if to_call > stack * 0.4 and tier == "trash":
            return ("fold", 0)
        if to_call > 0:
            return ("call", to_call)
        return ("check", 0)

    # Post-flop: always call unless facing more than half their stack
    if to_call > stack * 0.5:
        score = evaluate_hand(hole + community)
        if score[0] < ONE_PAIR:
            return ("fold", 0)
    if to_call > 0:
        return ("call", to_call)
    return ("check", 0)


def tight_passive(hole, community, pot, to_call, stack, position,
                  street, num_active, aggression):
    """
    Only enters with strong hands, but just calls — the classic "rock".
    Misses value by not raising. Easy to bluff off weak holdings.
    """
    tier = classify_hole_cards(hole)

    if street == "preflop":
        if tier in ("premium", "strong"):
            if to_call > 0:
                return ("call", to_call)
            return ("check", 0)
        if tier == "speculative" and to_call <= BIG_BLIND * 3:
            return ("call", to_call)
        if to_call == 0:
            return ("check", 0)
        return ("fold", 0)

    # Post-flop: call with top pair or better, fold the rest
    score = evaluate_hand(hole + community)
    if score[0] >= ONE_PAIR:
        if to_call <= pot * 0.5:
            return ("call", to_call)
        if score[0] >= TWO_PAIR:
            return ("call", min(to_call, stack))
    if to_call == 0:
        return ("check", 0)
    return ("fold", 0)


def tight_aggressive(hole, community, pot, to_call, stack, position,
                     street, num_active, aggression):
    """
    TAG: plays a narrow range of strong hands but bets and raises them
    hard. The most fundamentally sound strategy. Minimises variance while
    extracting maximum value from strong hands.
    """
    tier = classify_hole_cards(hole)

    if street == "preflop":
        if tier == "premium":
            bet = min(stack, BIG_BLIND * 4 + aggression * BIG_BLIND * 2)
            if to_call == 0 or aggression == 0:
                return ("raise", bet)
            return ("raise", min(stack, to_call + pot // 2))
        if tier == "strong":
            if aggression <= 1:
                return ("raise", min(stack, BIG_BLIND * 3))
            return ("call", to_call) if to_call <= BIG_BLIND * 6 else ("fold", 0)
        if tier == "speculative" and position >= 2 and to_call <= BIG_BLIND * 3:
            return ("call", to_call)
        if to_call == 0:
            return ("check", 0)
        return ("fold", 0)

    # Post-flop
    score = evaluate_hand(hole + community)
    hand_rank = score[0]

    if hand_rank >= TWO_PAIR:
        bet = min(stack, int(pot * 0.75))
        return ("raise", bet)
    if hand_rank == ONE_PAIR:
        if aggression == 0:
            return ("raise", min(stack, pot // 2))
        if to_call <= pot * 0.4:
            return ("call", to_call)
        return ("fold", 0)
    if to_call == 0:
        return ("check", 0)
    return ("fold", 0)


def loose_aggressive(hole, community, pot, to_call, stack, position,
                     street, num_active, aggression):
    """
    LAG: enters many pots and applies constant pressure through bets and
    raises. Hard to read. Wins big when it works; leaks chips when it
    doesn't. Effective in experienced fields, exploitable by stations.
    """
    tier = classify_hole_cards(hole)

    if street == "preflop":
        # Plays any non-trash hand, raises liberally
        if tier == "trash" and to_call > BIG_BLIND * 5:
            return ("fold", 0)
        if to_call == 0:
            return ("raise", BIG_BLIND * 3)
        if aggression <= 2:
            return ("raise", min(stack, to_call + pot // 3))
        return ("call", to_call)

    # Post-flop: bet most streets, give up on blanks after heavy resistance
    score = evaluate_hand(hole + community)
    hand_rank = score[0]

    if hand_rank >= ONE_PAIR:
        return ("raise", min(stack, int(pot * 0.8)))
    # Bluff on good board textures (low community cards = good for wide ranges)
    board_high = max((rank_val(c) for c in community), default=0)
    if board_high <= 7 and aggression == 0:  # low board, first to act
        return ("raise", min(stack, pot // 2))
    if to_call == 0:
        return ("check", 0)
    if to_call <= pot * 0.3:
        return ("call", to_call)
    return ("fold", 0)


def pot_odds_player(hole, community, pot, to_call, stack, position,
                    street, num_active, aggression):
    """
    Makes every decision based on pot odds vs estimated hand equity.
    Calls when equity > pot odds required, folds otherwise.
    Uses Monte Carlo equity estimation post-flop.
    Pre-flop uses a heuristic equity table.
    """
    if to_call == 0:
        # Free to see next card — always check, sometimes bet for value
        if community:
            score = evaluate_hand(hole + community)
            if score[0] >= TWO_PAIR:
                return ("raise", min(stack, pot // 2))
        return ("check", 0)

    # Pot odds: need equity > to_call / (pot + to_call)
    pot_odds_needed = to_call / (pot + to_call)

    if street == "preflop":
        equity = hole_card_equity(hole)
    else:
        # Use hand score as a fast proxy; only run Monte Carlo on river
        score = evaluate_hand(hole + community)
        if street == "river" or score[0] >= TWO_PAIR:
            equity = estimate_equity(hole, community, num_opponents=max(1, num_active - 1))
        else:
            # Approximate: scale hand rank 0-9 to rough equity 0.3-0.85
            equity = 0.30 + score[0] * 0.06

    if equity >= pot_odds_needed + 0.05:   # +5% margin of safety
        if equity >= 0.65 and aggression == 0:
            return ("raise", min(stack, int(pot * 0.7)))
        return ("call", to_call)

    return ("fold", 0)


def bluffer(hole, community, pot, to_call, stack, position,
            street, num_active, aggression):
    """
    Bets and raises with a wide range, regardless of hand strength.
    Bluffs frequently on all streets. Wins through fold equity.
    Very effective short-term; exploitable by patient callers.
    """
    tier = classify_hole_cards(hole)

    # Tight pre-flop range just so bluffs aren't trivially readable
    if street == "preflop":
        if tier in ("premium", "strong"):
            return ("raise", min(stack, BIG_BLIND * 4))
        if to_call <= BIG_BLIND * 3:
            # Call or raise speculative/marginal — set up bluffs post-flop
            return ("call", to_call) if random.random() < 0.4 else ("raise", min(stack, BIG_BLIND * 3))
        if to_call == 0:
            return ("raise", BIG_BLIND * 2)  # open every button/late
        return ("fold", 0) if tier == "trash" and to_call > BIG_BLIND * 4 else ("call", to_call)

    # Post-flop: bluff ~55% of the time regardless of hand
    score = evaluate_hand(hole + community)
    hand_rank = score[0]

    # Always bet strong hands
    if hand_rank >= TWO_PAIR:
        return ("raise", min(stack, int(pot * 0.9)))

    # Bluff with air ~55% frequency
    bluff_chance = 0.55
    if random.random() < bluff_chance and aggression <= 1:
        bet = min(stack, int(pot * random.uniform(0.5, 1.0)))
        return ("raise", bet)

    if to_call == 0:
        return ("check", 0)
    if to_call <= pot * 0.35 and hand_rank >= ONE_PAIR:
        return ("call", to_call)
    return ("fold", 0)


def position_aware(hole, community, pot, to_call, stack, position,
                   street, num_active, aggression):
    """
    Adjusts hand selection and aggression based on table position.
    Early position: only premiums. Late position: much wider range.
    Steals blinds from the button, 3-bets from the cutoff.
    Position is the single most important concept in poker strategy.
    """
    tier = classify_hole_cards(hole)
    pos_label = {0: "early", 1: "middle", 2: "late", 3: "blinds"}[position]

    if street == "preflop":
        # Early: very tight
        if position == 0:
            if tier == "premium":
                return ("raise", min(stack, BIG_BLIND * 4))
            if tier == "strong" and aggression == 0:
                return ("raise", min(stack, BIG_BLIND * 3))
            if to_call == 0:
                return ("check", 0)
            return ("fold", 0)

        # Middle: moderate range
        if position == 1:
            if tier in ("premium", "strong"):
                return ("raise", min(stack, BIG_BLIND * 3))
            if tier == "speculative" and to_call <= BIG_BLIND * 3:
                return ("call", to_call)
            if to_call == 0:
                return ("check", 0)
            return ("fold", 0)

        # Late / button: wide range, steal attempts
        if position == 2:
            if tier in ("premium", "strong"):
                return ("raise", min(stack, BIG_BLIND * 4))
            if tier in ("speculative", "marginal") and aggression == 0:
                return ("raise", min(stack, BIG_BLIND * 2 + BIG_BLIND // 2))
            if to_call <= BIG_BLIND * 3:
                return ("call", to_call)
            if to_call == 0:
                return ("raise", BIG_BLIND * 2)  # steal attempt
            return ("fold", 0)

        # Blinds: defend wider vs late raises
        if position == 3:
            if tier in ("premium", "strong"):
                return ("raise", min(stack, to_call * 3))
            if to_call <= BIG_BLIND * 4 and tier != "trash":
                return ("call", to_call)
            if to_call == 0:
                return ("check", 0)
            return ("fold", 0)

    # Post-flop: bet in position, check OOP with marginal hands
    score = evaluate_hand(hole + community)
    hand_rank = score[0]

    if hand_rank >= TWO_PAIR:
        return ("raise", min(stack, int(pot * 0.75)))
    if hand_rank == ONE_PAIR:
        if position >= 2:  # in position — bet for value/protection
            return ("raise", min(stack, pot // 2)) if aggression == 0 else ("call", to_call)
        if to_call <= pot * 0.35:
            return ("call", to_call)
        return ("fold", 0)
    if to_call == 0:
        return ("check", 0)
    # Fold air out of position, occasional float in position
    if position >= 2 and to_call <= pot * 0.3:
        return ("call", to_call)
    return ("fold", 0)


def gto_balanced(hole, community, pot, to_call, stack, position,
                 street, num_active, aggression):
    """
    Approximates GTO (Game Theory Optimal) play using mixed strategies.
    Balances value bets with bluffs at theoretically correct frequencies.
    Uses ~70% value / 30% bluff ratio, sizes bets at ~67% pot, and
    defends against bets at the minimum defence frequency (MDF).
    Not perfect GTO — a real solver would be needed — but captures
    the key principles: balanced ranges, correct bet sizing, MDF defence.
    """
    tier = classify_hole_cards(hole)

    if street == "preflop":
        # GTO open-raising ranges: wider from late, tighter from early
        open_thresholds = {0: ("premium",), 1: ("premium", "strong"),
                           2: ("premium", "strong", "speculative"),
                           3: ("premium", "strong", "speculative", "marginal")}
        valid_tiers = open_thresholds.get(position, ("premium", "strong"))

        if tier in valid_tiers:
            if aggression == 0:
                return ("raise", min(stack, BIG_BLIND * 3))
            if aggression == 1 and tier in ("premium", "strong"):
                # 3-bet balanced: value + some bluffs
                return ("raise", min(stack, to_call * 3))
            if to_call <= BIG_BLIND * 5 and tier in valid_tiers:
                return ("call", to_call)
            return ("fold", 0)

        if to_call == 0:
            return ("check", 0)
        # MDF: call enough to prevent profitable bluffs
        mdf = pot / (pot + to_call)
        if random.random() < mdf * 0.5 and tier in ("speculative", "marginal"):
            return ("call", to_call)
        return ("fold", 0)

    # Post-flop GTO principles
    score = evaluate_hand(hole + community)
    hand_rank = score[0]
    # Fast equity proxy: only run Monte Carlo on river with strong hands
    if street == "river" and hand_rank >= ONE_PAIR:
        equity = estimate_equity(hole, community, num_opponents=max(1, num_active - 1))
    else:
        equity = 0.30 + hand_rank * 0.06  # fast heuristic

    # Bet sizing: ~67% pot with balanced range
    bet_size = min(stack, int(pot * 0.67))

    if to_call == 0:
        # Betting range: value hands + bluffs at correct ratio (~2:1)
        if hand_rank >= TWO_PAIR:
            return ("raise", bet_size)  # value
        if hand_rank == ONE_PAIR and equity >= 0.55:
            return ("raise", bet_size)  # thin value
        # Bluff at ~30% frequency with good blockers / equity
        if equity >= 0.30 and random.random() < 0.30:
            return ("raise", bet_size)
        return ("check", 0)

    # Facing a bet: use MDF (minimum defence frequency)
    # MDF = pot / (pot + bet) — defend this fraction of range
    mdf = pot / (pot + to_call)

    if hand_rank >= TWO_PAIR:
        # Always continue with strong hands; raise for value sometimes
        if equity >= 0.70 and random.random() < 0.4:
            return ("raise", min(stack, to_call + int(pot * 0.67)))
        return ("call", to_call)

    if hand_rank == ONE_PAIR:
        if random.random() < mdf:
            return ("call", to_call)
        return ("fold", 0)

    # Weak hands: defend at MDF frequency with draws/equity
    if equity >= 0.40 and random.random() < mdf * 0.6:
        return ("call", to_call)
    return ("fold", 0)


# Map strategy name → function
STRATEGY_MAP = {
    "calling_station":  calling_station,
    "tight_passive":    tight_passive,
    "tight_aggressive": tight_aggressive,
    "loose_aggressive": loose_aggressive,
    "pot_odds_player":  pot_odds_player,
    "bluffer":          bluffer,
    "position_aware":   position_aware,
    "gto_balanced":     gto_balanced,
}


# ─────────────────────────────────────────────────────────────────
#  PLAYER CLASS
# ─────────────────────────────────────────────────────────────────

class Player:
    def __init__(self, name, strategy_name, seat):
        self.name          = name
        self.strategy_name = strategy_name
        self.strategy_fn   = STRATEGY_MAP[strategy_name]
        self.seat          = seat
        self.stack         = STARTING_STACK
        self.hole_cards    = []
        self.folded        = False
        self.all_in        = False
        self.bet_this_street = 0
        self.rebuys        = 0

    def reset_for_hand(self):
        self.hole_cards        = []
        self.folded            = False
        self.all_in            = False
        self.bet_this_street   = 0

    def act(self, community, pot, to_call, position, street, num_active, aggression):
        if self.folded or self.all_in:
            return ("check", 0)

        actual_to_call = min(to_call, self.stack)
        action, amount = self.strategy_fn(
            self.hole_cards, community, pot, actual_to_call,
            self.stack, position, street, num_active, aggression
        )

        # Enforce legal actions
        if action == "fold":
            self.folded = True
            return ("fold", 0)

        if action == "check":
            if actual_to_call > 0:
                # Can't check when there's a bet — treat as call
                action = "call"
                amount = actual_to_call
            else:
                return ("check", 0)

        if action == "call":
            amount = min(actual_to_call, self.stack)
            self.stack         -= amount
            self.bet_this_street += amount
            if self.stack == 0:
                self.all_in = True
            return ("call", amount)

        if action in ("raise", "all_in"):
            # Must at least call + min-raise (= 1 BB on top)
            min_raise = actual_to_call + BIG_BLIND
            amount = max(amount, min_raise)
            amount = min(amount, self.stack)
            self.stack         -= amount
            self.bet_this_street += amount
            if self.stack == 0:
                self.all_in = True
                return ("all_in", amount)
            return ("raise", amount)

        return ("check", 0)


# ─────────────────────────────────────────────────────────────────
#  HAND ENGINE — plays one complete hand of Texas Hold'em
# ─────────────────────────────────────────────────────────────────

class HandEngine:
    def __init__(self, players):
        self.players = players

    def play_hand(self, dealer_idx):
        """
        Plays one complete hand. Returns a dict mapping player name → net chips won/lost.
        dealer_idx determines position (button).
        """
        n       = len(self.players)
        active  = [p for p in self.players if p.stack > 0]

        # Rebuy busted players if allowed
        if ALLOW_REBUYS:
            for p in self.players:
                if p.stack == 0:
                    p.stack  = STARTING_STACK
                    p.rebuys += 1
            active = list(self.players)

        if len(active) < 2:
            return {p.name: 0 for p in self.players}

        for p in active:
            p.reset_for_hand()

        # Deal hole cards
        deck = make_deck()
        random.shuffle(deck)
        card_idx = 0
        for p in active:
            p.hole_cards = [deck[card_idx], deck[card_idx + 1]]
            card_idx += 2

        community = []
        pot       = 0
        side_pots = []  # simplified — track main pot only for now

        # Post blinds
        sb_idx = dealer_idx % len(active)
        bb_idx = (dealer_idx + 1) % len(active)
        sb_player = active[sb_idx]
        bb_player = active[bb_idx]

        sb_amount = min(SMALL_BLIND, sb_player.stack)
        sb_player.stack -= sb_amount
        sb_player.bet_this_street = sb_amount
        pot += sb_amount

        bb_amount = min(BIG_BLIND, bb_player.stack)
        bb_player.stack -= bb_amount
        bb_player.bet_this_street = bb_amount
        pot += bb_amount

        starting_stacks = {p.name: p.stack + p.bet_this_street for p in active}

        # ── Betting streets ──────────────────────────────────────
        streets = [
            ("preflop",  [],            dealer_idx + 2),  # UTG acts first preflop
            ("flop",     slice(card_idx, card_idx + 3),   dealer_idx),
            ("turn",     slice(card_idx + 3, card_idx + 4), dealer_idx),
            ("river",    slice(card_idx + 4, card_idx + 5), dealer_idx),
        ]

        for street_name, card_slice, first_actor_idx in streets:
            # Deal community cards
            if street_name == "flop":
                community = [deck[card_idx], deck[card_idx+1], deck[card_idx+2]]
            elif street_name == "turn":
                community.append(deck[card_idx + 3])
            elif street_name == "river":
                community.append(deck[card_idx + 4])

            still_in = [p for p in active if not p.folded]
            if len(still_in) <= 1:
                break

            # Reset street bets (carry over BB on preflop)
            if street_name != "preflop":
                for p in active:
                    p.bet_this_street = 0

            pot = self._betting_round(
                active, still_in, community, pot,
                street_name, first_actor_idx, bb_amount if street_name == "preflop" else 0
            )

            still_in = [p for p in active if not p.folded]
            if len(still_in) <= 1:
                break

        # ── Showdown ─────────────────────────────────────────────
        still_in = [p for p in active if not p.folded]
        results  = {p.name: 0 for p in self.players}

        if len(still_in) == 1:
            winner = still_in[0]
            results[winner.name] = pot
            winner.stack += pot
        else:
            # Evaluate hands and split pot
            scores = [(p, evaluate_hand(p.hole_cards + community)) for p in still_in]
            scores.sort(key=lambda x: x[1], reverse=True)
            best_score = scores[0][1]
            winners = [p for p, s in scores if s == best_score]
            share = pot // len(winners)
            remainder = pot - share * len(winners)
            for p in winners:
                p.stack += share
                results[p.name] += share
            # Give remainder chip to first winner (standard rule)
            if remainder and winners:
                winners[0].stack += remainder
                results[winners[0].name] += remainder

        # Convert results to net chips (won - contributed)
        net = {}
        for p in active:
            contributed = starting_stacks[p.name] - p.stack + results.get(p.name, 0)
            net[p.name] = results.get(p.name, 0) - contributed

        # Players not in this hand (busted, no stack)
        for p in self.players:
            if p.name not in net:
                net[p.name] = 0

        return net

    def _betting_round(self, active, still_in, community, pot,
                       street, first_actor_idx, current_bet):
        """
        Runs a single betting round. Returns updated pot.
        """
        n           = len(active)
        aggression  = 0
        current_bet = current_bet  # chips to call
        last_raiser = None

        # Build acting order
        order = []
        for i in range(n):
            idx = (first_actor_idx + i) % n
            p   = active[idx]
            if not p.folded and not p.all_in:
                order.append((idx, p))

        if not order:
            return pot

        acted  = set()
        i      = 0
        loops  = 0

        while loops < n * 4:  # safety cap
            loops += 1
            if not order:
                break

            idx, p = order[i % len(order)]
            i      += 1

            if p.folded or p.all_in:
                continue

            still_in_now = [x for x in active if not x.folded]
            if len(still_in_now) <= 1:
                break

            to_call = max(0, current_bet - p.bet_this_street)

            # Position: 0=early, 1=mid, 2=late, 3=blinds (simplified)
            pos_idx   = list(active).index(p)
            num_seats = len(active)
            if pos_idx < num_seats // 3:
                position = 0
            elif pos_idx < 2 * num_seats // 3:
                position = 1
            else:
                position = 2

            action, amount = p.act(
                community, pot, to_call, position,
                street, len(still_in_now), aggression
            )

            if action == "fold":
                acted.add(p.name)
                still_in_now = [x for x in active if not x.folded]
                if len(still_in_now) == 1:
                    break
                continue

            if action in ("raise", "all_in"):
                pot         += amount
                current_bet  = p.bet_this_street
                aggression  += 1
                last_raiser  = p.name
                acted        = {p.name}  # others need to act again
            elif action in ("call", "check"):
                pot += amount
                acted.add(p.name)

            # Check if action is complete: all non-folded, non-allin players
            # have acted and matched the current bet
            eligible = [x for x in active if not x.folded and not x.all_in]
            all_matched = all(
                x.bet_this_street >= current_bet or x.stack == 0
                for x in eligible
            )
            all_acted = all(x.name in acted for x in eligible)

            if all_matched and all_acted:
                break

        return pot


# ─────────────────────────────────────────────────────────────────
#  SIMULATION
# ─────────────────────────────────────────────────────────────────

class Simulation:
    def __init__(self):
        self.players = [Player(name, strat, i) for i, (name, strat) in enumerate(PLAYERS)]
        self.engine  = HandEngine(self.players)

        pnames = [name for name, _ in PLAYERS]

        self.net_per_hand     = defaultdict(list)   # net chips each hand
        self.hands_won        = defaultdict(int)
        self.hands_played     = defaultdict(int)
        self.showdowns_won    = defaultdict(int)
        self.showdowns_played = defaultdict(int)
        self.vpip             = defaultdict(int)     # voluntarily put chips in pot
        self.pfr              = defaultdict(int)     # pre-flop raise
        self.total_won        = defaultdict(float)
        self.total_lost       = defaultdict(float)
        self.biggest_pot_won  = defaultdict(float)
        self.bust_count       = defaultdict(int)

        # Track hand win types
        self.hand_type_wins = defaultdict(lambda: defaultdict(int))

        self.dealer_idx = 0

    def run(self):
        for hand_num in range(NUM_HANDS):
            results = self.engine.play_hand(self.dealer_idx)
            self._record(results)
            self.dealer_idx = (self.dealer_idx + 1) % len(self.players)

    def _record(self, results):
        for p in self.players:
            name = p.name
            net  = results.get(name, 0)
            self.net_per_hand[name].append(net)

            if net > 0:
                self.hands_won[name]   += 1
                self.total_won[name]   += net
                self.biggest_pot_won[name] = max(self.biggest_pot_won[name], net)
            elif net < 0:
                self.total_lost[name] += abs(net)

            if net != 0 or p.bet_this_street > 0:
                self.hands_played[name] += 1

    # ─────────────────────────────────────────────────────────────
    #  REPORT
    # ─────────────────────────────────────────────────────────────

    def report(self):
        W    = 68
        sep  = "─" * W
        sep2 = "━" * W

        def pct(n, d):
            return f"{n / d * 100:.1f}%" if d else "n/a"

        def bb(chips):
            """Convert chips to big blinds."""
            return chips / BIG_BLIND

        def bb_str(chips):
            v = bb(chips)
            return f"{v:+.1f} BB"

        # ── Header ───────────────────────────────────────────────
        print(f"\n{'═' * W}")
        print(f"  ♠♥  TEXAS HOLD'EM SIMULATION REPORT  ♦♣")
        print(f"{'═' * W}")
        print(f"  Hands simulated  : {NUM_HANDS:,}")
        print(f"  Players at table : {len(self.players)}")
        print(f"  Blinds           : {SMALL_BLIND}/{BIG_BLIND} chips")
        print(f"  Starting stack   : {STARTING_STACK} chips  ({STARTING_STACK // BIG_BLIND} BB)")
        print(f"  Rebuys           : {'allowed (infinite)' if ALLOW_REBUYS else 'not allowed'}")

        # ── Per-player sections ───────────────────────────────────
        STRATEGY_DESCRIPTIONS = {
            "calling_station":  (
                "Calls almost everything. Rarely raises. Sees every flop.",
                "Classic 'fish' — profitable to play against, very unprofitable to be.",
            ),
            "tight_passive":    (
                "Only plays premium hands, but just calls instead of raising.",
                "Misses value badly. Easy to bluff off hands. The 'rock'.",
            ),
            "tight_aggressive": (
                "Narrow starting range + bets and raises hard for value.",
                "TAG: the most fundamentally sound baseline strategy.",
            ),
            "loose_aggressive": (
                "Enters many pots and applies constant bet/raise pressure.",
                "LAG: hard to read; effective vs thinking players, leaky vs stations.",
            ),
            "pot_odds_player":  (
                "Calls only when equity > pot odds required. Folds otherwise.",
                "Mathematically disciplined. Uses Monte Carlo equity estimates post-flop.",
            ),
            "bluffer":          (
                "Bets and raises regardless of hand strength. ~55% bluff frequency.",
                "Wins through fold equity. Exploitable by patient calling stations.",
            ),
            "position_aware":   (
                "Tight from early position, wide and aggressive from late position.",
                "Exploits the power of position — acts last and has more information.",
            ),
            "gto_balanced":     (
                "Balanced betting ranges, ~67% pot sizing, MDF-based defence.",
                "Approximates game-theory optimal: unexploitable but not maximally exploitative.",
            ),
        }

        for name, strategy_name in PLAYERS:
            nets   = self.net_per_hand[name]
            rounds = len(nets)
            if not rounds:
                continue

            total_net   = sum(nets)
            won         = self.hands_won[name]
            win_pct     = won / rounds * 100 if rounds else 0
            avg_net     = statistics.mean(nets)
            net_bb_100  = (avg_net / BIG_BLIND) * 100   # BB/100 hands — standard poker metric
            stdev       = statistics.stdev(nets) if len(nets) > 1 else 0

            desc1, desc2 = STRATEGY_DESCRIPTIONS.get(strategy_name, ("",""))

            print(f"\n{sep2}")
            print(f"  {name.upper()}  [{strategy_name.upper()}]")
            print(sep2)
            print(f"  {desc1}")
            print(f"  {desc2}")
            print()

            print(f"  RESULTS over {rounds:,} hands:")
            print(f"  Hands won          : {won:,}  ({win_pct:.1f}%)")
            print(f"  Net chips          : {total_net:>+,.0f}")
            print(f"  Net in BB          : {bb_str(total_net)}")
            print(f"  BB/100 hands       : {net_bb_100:>+.2f}  ← the standard poker win-rate metric")
            print(f"  Avg net per hand   : {avg_net:>+.2f} chips  ({bb_str(avg_net)})")
            print(f"  Biggest pot won    : {self.biggest_pot_won[name]:,.0f} chips  "
                  f"({bb(self.biggest_pot_won[name]):.0f} BB)")
            print(f"  Total chips won    : {self.total_won[name]:,.0f}")
            print(f"  Total chips lost   : {self.total_lost[name]:,.0f}")
            print(f"  Rebuys             : {self.players[[p.name for p in self.players].index(name)].rebuys}")
            print()

            # Variance / streaks
            wins_in_row  = 0; best_w = 0
            loss_in_row  = 0; best_l = 0
            for net in nets:
                if net > 0:
                    wins_in_row += 1; loss_in_row = 0
                    best_w = max(best_w, wins_in_row)
                elif net < 0:
                    loss_in_row += 1; wins_in_row = 0
                    best_l = max(best_l, loss_in_row)

            profitable  = sum(1 for n in nets if n > 0)
            losing      = sum(1 for n in nets if n < 0)
            breakeven   = sum(1 for n in nets if n == 0)

            print(f"  VARIANCE & STREAKS:")
            print(f"  Profitable hands   : {profitable:,}  ({pct(profitable, rounds)})")
            print(f"  Losing hands       : {losing:,}  ({pct(losing, rounds)})")
            print(f"  Break-even hands   : {breakeven:,}  ({pct(breakeven, rounds)})")
            print(f"  Std dev per hand   : {stdev:.2f} chips")
            print(f"  Longest win streak : {best_w} hands in a row")
            print(f"  Longest loss streak: {best_l} hands in a row")

        # ── Head-to-head comparison ───────────────────────────────
        print(f"\n{'═' * W}")
        print("  HEAD-TO-HEAD COMPARISON")
        print(f"{'═' * W}")
        print(f"  {'Player':<20} {'Strategy':<18} {'Win%':>6}  {'BB/100':>8}  "
              f"{'Net BB':>8}  {'Rebuys':>6}")
        print(f"  {sep}")

        bb100s = {}
        for name, strategy_name in PLAYERS:
            nets    = self.net_per_hand[name]
            rounds  = len(nets)
            won     = self.hands_won[name]
            avg_net = statistics.mean(nets) if nets else 0
            bb100   = (avg_net / BIG_BLIND) * 100
            bb100s[name] = bb100
            net_bb  = bb(sum(nets))
            p_obj   = self.players[[p.name for p in self.players].index(name)]

            print(f"  {name:<20} {strategy_name:<18} "
                  f"{won / rounds * 100 if rounds else 0:>5.1f}%  "
                  f"{bb100:>+8.2f}  "
                  f"{net_bb:>+8.1f}  "
                  f"{p_obj.rebuys:>6}")

        print()
        print("  What this tells us:")
        best  = max(bb100s, key=bb100s.get)
        worst = min(bb100s, key=bb100s.get)
        print(f"  • {best} had the highest BB/100 — best overall performer.")
        print(f"  • {worst} had the lowest BB/100 — biggest net loser.")

        print(f"\n  Strategy ranking by BB/100 (higher = better):")
        ranked = sorted(PLAYERS, key=lambda p: bb100s[p[0]], reverse=True)
        for rank, (name, strat) in enumerate(ranked, 1):
            marker = " ← best" if rank == 1 else (" ← worst" if rank == len(ranked) else "")
            print(f"    {rank}. {name:<22} {bb100s[name]:>+8.2f} BB/100{marker}")

        print()
        print("  Key concepts illustrated by this simulation:")
        print("  • BB/100 is the standard poker win-rate metric (big blinds won per 100 hands).")
        print("  • In this closed simulation, rebuys inflate absolute chip numbers —")
        print("    the BB/100 rankings are meaningful for comparison, not as absolute values.")
        print("  • A live poker win rate of +5 BB/100 is considered strong.")
        print("  • Online regulars often run +2 to +8 BB/100 at their stakes.")
        print("  • High variance means large swings even for winning strategies.")
        print("  • Position, hand selection, and bet sizing are the three pillars of poker.")

        print(f"\n{'═' * W}\n")


# ─────────────────────────────────────────────────────────────────
#  RUN IT
# ─────────────────────────────────────────────────────────────────

sim = Simulation()
sim.run()
sim.report()