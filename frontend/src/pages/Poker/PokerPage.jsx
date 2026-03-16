import { useState } from 'react';
import { pokerApi } from '../../utils/api';
import LoadingSpinner from '../../components/LoadingSpinner/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage/ErrorMessage';
import styles from '../Blackjack/BlackjackPage.module.css';

const PokerPage = () => {
  const [config, setConfig] = useState({
    num_hands: 10000,
    num_players: 6,
    small_blind: 1,
    big_blind: 2,
    starting_stack: 200,
    allow_rebuys: true,
    players: ['tight_aggressive', 'loose_aggressive', 'tight_passive', 'calling_station'],
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const availableStrategies = [
    { value: 'calling_station', label: 'Calling Station' },
    { value: 'tight_passive', label: 'Tight Passive' },
    { value: 'tight_aggressive', label: 'Tight Aggressive' },
    { value: 'loose_aggressive', label: 'Loose Aggressive' },
    { value: 'pot_odds_player', label: 'Pot Odds Player' },
    { value: 'bluffer', label: 'Bluffer' },
    { value: 'position_aware', label: 'Position Aware' },
    { value: 'gto_balanced', label: 'GTO Balanced' },
  ];

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setConfig((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : parseInt(value),
    }));
  };

  const handleStrategyToggle = (strategy) => {
    setConfig((prev) => {
      const newPlayers = prev.players.includes(strategy)
        ? prev.players.filter((s) => s !== strategy)
        : [...prev.players, strategy];
      
      // Update num_players to match selected strategies
      return {
        ...prev,
        players: newPlayers,
        num_players: newPlayers.length,
      };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await pokerApi.simulate(config);
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to run simulation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>♠️ Poker Simulation</h1>
        <p>Test poker strategies in Texas Hold'em</p>
      </header>

      <div className={styles.content}>
        <aside className={styles.sidebar}>
          <form onSubmit={handleSubmit} className={styles.form}>
            <h2>Configuration</h2>

            <div className={styles.formGroup}>
              <label htmlFor="num_hands">Number of Hands</label>
              <input
                type="number"
                id="num_hands"
                name="num_hands"
                value={config.num_hands}
                onChange={handleInputChange}
                min="100"
                max="100000"
                step="1"
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="small_blind">Small Blind</label>
              <input
                type="number"
                id="small_blind"
                name="small_blind"
                value={config.small_blind}
                onChange={handleInputChange}
                min="1"
                max="100"
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="big_blind">Big Blind</label>
              <input
                type="number"
                id="big_blind"
                name="big_blind"
                value={config.big_blind}
                onChange={handleInputChange}
                min="2"
                max="200"
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="starting_stack">Starting Stack</label>
              <input
                type="number"
                id="starting_stack"
                name="starting_stack"
                value={config.starting_stack}
                onChange={handleInputChange}
                min="50"
                max="10000"
                step="50"
                required
              />
            </div>

            <div className={styles.checkboxGroup}>
              <label>
                <input
                  type="checkbox"
                  name="allow_rebuys"
                  checked={config.allow_rebuys}
                  onChange={handleInputChange}
                />
                <span>Allow rebuys</span>
              </label>
            </div>

            <div className={styles.formGroup}>
              <label>Player Strategies ({config.players.length} selected)</label>
              <div className={styles.strategiesGrid}>
                {availableStrategies.map((strategy) => (
                  <button
                    key={strategy.value}
                    type="button"
                    className={`${styles.strategyButton} ${
                      config.players.includes(strategy.value) ? styles.active : ''
                    }`}
                    onClick={() => handleStrategyToggle(strategy.value)}
                  >
                    {strategy.label}
                  </button>
                ))}
              </div>
            </div>

            <button type="submit" className={styles.submitButton} disabled={loading || config.players.length < 2}>
              {loading ? 'Running...' : 'Run Simulation'}
            </button>
          </form>
        </aside>

        <main className={styles.main}>
          {loading && <LoadingSpinner message="Running poker simulation..." />}
          {error && <ErrorMessage message={error} onRetry={handleSubmit} />}
          {results && (
            <div className={styles.results}>
              <h2>Results</h2>
              <div className={styles.resultsHeader}>
                <div className={styles.stat}>
                  <span className={styles.statLabel}>Total Hands</span>
                  <span className={styles.statValue}>{results.total_hands.toLocaleString()}</span>
                </div>
                <div className={styles.stat}>
                  <span className={styles.statLabel}>Total Pots</span>
                  <span className={styles.statValue}>{results.total_pots.toLocaleString()}</span>
                </div>
                <div className={styles.stat}>
                  <span className={styles.statLabel}>Avg Pot Size</span>
                  <span className={styles.statValue}>{results.average_pot_size}</span>
                </div>
                <div className={styles.stat}>
                  <span className={styles.statLabel}>Execution Time</span>
                  <span className={styles.statValue}>{results.execution_time}s</span>
                </div>
              </div>

              <div className={styles.playersTable}>
                <table>
                  <thead>
                    <tr>
                      <th>Strategy</th>
                      <th>Hands</th>
                      <th>Wins</th>
                      <th>Win Rate</th>
                      <th>VPIP</th>
                      <th>Net Profit</th>
                      <th>Avg Pot Won</th>
                      <th>Biggest Pot</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.player_stats.map((player) => (
                      <tr key={player.name}>
                        <td className={styles.strategyName}>{player.name}</td>
                        <td>{player.hands_played.toLocaleString()}</td>
                        <td>{player.hands_won.toLocaleString()}</td>
                        <td>{player.win_rate.toFixed(2)}%</td>
                        <td>{player.vpip.toFixed(2)}%</td>
                        <td className={player.net_profit >= 0 ? styles.positive : styles.negative}>
                          {player.net_profit >= 0 ? '+' : ''}{player.net_profit}
                        </td>
                        <td>{player.avg_pot_won}</td>
                        <td>{player.biggest_pot}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default PokerPage;
