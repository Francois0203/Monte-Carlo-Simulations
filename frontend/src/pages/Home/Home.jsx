import { Link } from 'react-router-dom';
import { GiCardJoker, GiCardRandom, GiSnake, GiTicTacToe } from 'react-icons/gi';
import { FaArrowRight } from 'react-icons/fa';
import styles from './Home.module.css';

const SIMULATIONS = [
  {
    path: '/blackjack',
    title: 'Blackjack',
    icon: GiCardJoker,
    description: 'Compare 8 strategies — from Basic Strategy to Card Counting. Discover the real house edge over thousands of hands.',
    color: '#3b82f6',
    gradient: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
    tags: ['8 strategies', 'Card counting', 'ROI analysis'],
  },
  {
    path: '/poker',
    title: "Texas Hold'em",
    icon: GiCardRandom,
    description: "Pit 8 player archetypes head-to-head. See which style — TAG, LAG, GTO, Bluffer — dominates in the long run.",
    color: '#8b5cf6',
    gradient: 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)',
    tags: ['8 player types', 'VPIP & PFR', 'Stack dynamics'],
  },
  {
    path: '/snakes-and-ladders',
    title: 'Snakes & Ladders',
    icon: GiSnake,
    description: 'Pure probability — no decisions, only dice rolls. Analyse game length distributions and turn-order advantage.',
    color: '#f59e0b',
    gradient: 'linear-gradient(135deg, #f59e0b 0%, #b45309 100%)',
    tags: ['Configurable board', 'Multi-player', 'Length analysis'],
  },
  {
    path: '/naughts-and-crosses',
    title: 'Tic-Tac-Toe',
    icon: GiTicTacToe,
    description: 'Both players choose randomly. Quantify the first-mover advantage and draw rates across 3×3, 4×4 and 5×5 boards.',
    color: '#06b6d4',
    gradient: 'linear-gradient(135deg, #06b6d4 0%, #0e7490 100%)',
    tags: ['3 board sizes', 'First-mover edge', 'Draw analysis'],
  },
];

export default function Home() {
  return (
    <div className={styles.home}>
      {/* Hero */}
      <section className={styles.hero}>
        <div className={styles.heroInner}>
          <span className={styles.badge}>Monte Carlo Method</span>
          <h1 className={styles.title}>
            Simulate. Analyse.<br />
            <span className={styles.titleGradient}>Understand Probability.</span>
          </h1>
          <p className={styles.subtitle}>
            Configure parameters and run up to 100,000 iterations of four classic games.
            Watch patterns emerge from randomness with interactive real-time charts.
          </p>

          <div className={styles.heroMeta}>
            <div className={styles.heroMetaItem}>
              <span className={styles.heroMetaValue}>100k</span>
              <span className={styles.heroMetaLabel}>Max iterations</span>
            </div>
            <div className={styles.heroMetaDivider} />
            <div className={styles.heroMetaItem}>
              <span className={styles.heroMetaValue}>4</span>
              <span className={styles.heroMetaLabel}>Simulations</span>
            </div>
            <div className={styles.heroMetaDivider} />
            <div className={styles.heroMetaItem}>
              <span className={styles.heroMetaValue}>Real-time</span>
              <span className={styles.heroMetaLabel}>Results & charts</span>
            </div>
          </div>
        </div>
      </section>

      {/* Cards */}
      <section className={styles.grid}>
        {SIMULATIONS.map((sim, i) => {
          const Icon = sim.icon;
          return (
            <Link
              key={sim.path}
              to={sim.path}
              className={styles.card}
              style={{
                '--card-color': sim.color,
                '--card-gradient': sim.gradient,
                animationDelay: `${i * 0.07}s`,
              }}
            >
              {/* Top accent bar — expands on hover via CSS */}
              <span className={styles.cardBar} />

              <div className={styles.cardTop}>
                <div className={styles.cardIcon}><Icon /></div>
                <span className={styles.cardArrow}><FaArrowRight /></span>
              </div>

              <h2 className={styles.cardTitle}>{sim.title}</h2>
              <p className={styles.cardDesc}>{sim.description}</p>

              <div className={styles.cardTags}>
                {sim.tags.map(tag => (
                  <span key={tag} className={styles.cardTag}>{tag}</span>
                ))}
              </div>
            </Link>
          );
        })}
      </section>
    </div>
  );
}
