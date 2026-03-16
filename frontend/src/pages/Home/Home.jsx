import { Link } from 'react-router-dom';
import styles from './Home.module.css';

const Home = () => {
  const simulations = [
    {
      title: 'Blackjack',
      icon: '🃏',
      description: 'Simulate different blackjack strategies and compare their effectiveness.',
      features: ['8 player strategies', 'Configurable rules', 'Card counting analysis'],
      path: '/blackjack',
      color: '#ef4444',
    },
    {
      title: 'Poker',
      icon: '♠️',
      description: 'Test poker strategies in Texas Hold\'em with various player types.',
      features: ['8 player styles', 'Blind control', 'VPIP & PFR tracking'],
      path: '/poker',
      color: '#10b981',
    },
    {
      title: 'Snakes & Ladders',
      icon: '🎲',
      description: 'Analyze probabilities in this classic board game.',
      features: ['Custom board size', 'Configurable obstacles', 'Bounce-back rule'],
      path: '/snakes-and-ladders',
      color: '#f59e0b',
    },
    {
      title: 'Tic-Tac-Toe',
      icon: '⭕',
      description: 'Explore random play outcomes in Naughts and Crosses.',
      features: ['Multiple board sizes', 'Win probability', 'Position analysis'],
      path: '/naughts-and-crosses',
      color: '#8b5cf6',
    },
  ];

  return (
    <div className={styles.home}>
      <header className={styles.hero}>
        <h1 className={styles.heroTitle}>Monte Carlo Simulations</h1>
        <p className={styles.heroSubtitle}>
          Run statistical simulations for various games and analyze the results with configurable parameters
        </p>
      </header>

      <div className={styles.grid}>
        {simulations.map((sim) => (
          <Link
            key={sim.path}
            to={sim.path}
            className={styles.card}
            style={{ '--card-color': sim.color }}
          >
            <div className={styles.cardIcon}>{sim.icon}</div>
            <h2 className={styles.cardTitle}>{sim.title}</h2>
            <p className={styles.cardDescription}>{sim.description}</p>
            <ul className={styles.features}>
              {sim.features.map((feature, index) => (
                <li key={index} className={styles.feature}>
                  ✓ {feature}
                </li>
              ))}
            </ul>
            <div className={styles.cardFooter}>
              <span className={styles.cardButton}>
                Start Simulation →
              </span>
            </div>
          </Link>
        ))}
      </div>

      <section className={styles.info}>
        <h2>About Monte Carlo Simulations</h2>
        <p>
          Monte Carlo simulations use repeated random sampling to obtain numerical results. 
          This approach is particularly useful for understanding the probability distributions 
          of different outcomes in complex systems where analytical solutions are difficult 
          to obtain.
        </p>
        <p>
          Each simulation runs thousands of games with different strategies and configurations, 
          providing statistical insights into optimal play, win rates, and expected outcomes.
        </p>
      </section>
    </div>
  );
};

export default Home;
