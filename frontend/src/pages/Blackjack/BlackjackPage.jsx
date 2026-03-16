import { useState } from 'react';
import { GiCardJoker } from 'react-icons/gi';
import { blackjackApi } from '../../utils/api';
import LoadingSpinner from '../../components/LoadingSpinner/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage/ErrorMessage';
import styles from './BlackjackPage.module.css';

const BlackjackPage = () => {
  const [config, setConfig] = useState({
    num_games: 10000,
    num_decks: 6,
    blackjack_payout: 1.5,
    dealer_stands_soft: true,
    allow_splits: true,
    allow_double_down: true,
    ace_high: true,
    players: ['basic', 'aggressive', 'card_counter', 'martingale'],
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const availableStrategies = [
    { value: 'never_bust', label: 'Never Bust' },
    { value: 'safe', label: 'Safe Player' },
    { value: 'basic', label: 'Basic Strategy' },
    { value: 'aggressive', label: 'Aggressive' },
    { value: 'mimic_dealer', label: 'Mimic Dealer' },
    { value: 'gut_feel', label: 'Gut Feel' },
    { value: 'card_counter', label: 'Card Counter' },
    { value: 'martingale', label: 'Martingale' },
  ];

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setConfig((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : type === 'number' ? parseFloat(value) : value,
    }));
  };

  const handleStrategyToggle = (strategy) => {
    setConfig((prev) => ({
      ...prev,
      players: prev.players.includes(strategy)
        ? prev.players.filter((s) => s !== strategy)
        : [...prev.players, strategy],
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await blackjackApi.simulate(config);
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
        <h1><GiCardJoker className={styles.icon} /> Blackjack Simulation</h1>
        <p>Compare different blackjack strategies with configurable rules</p>
      </header>

      <div className={styles.content}>
        <aside className={styles.sidebar}>
          <form onSubmit={handleSubmit} className={styles.form}>
            <h2>Configuration</h2>

            <div className={styles.formGroup}>
              <label htmlFor="num_games">Number of Games</label>
              <input
                type="number"
                id="num_games"
                name="num_games"
                value={config.num_games}
                onChange={handleInputChange}
                min="100"
                max="100000"
                step="1"
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="num_decks">Number of Decks</label>
              <input
                type="number"
                id="num_decks"
                name="num_decks"
                value={config.num_decks}
                onChange={handleInputChange}
                min="1"
                max="8"
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="blackjack_payout">Blackjack Payout</label>
              <select
                id="blackjack_payout"
                name="blackjack_payout"
                value={config.blackjack_payout}
                onChange={handleInputChange}
              >
                <option value={1.5}>3:2 (1.5x)</option>
                <option value={1.2}>6:5 (1.2x)</option>
                <option value={2.0}>2:1 (2.0x)</option>
              </select>
            </div>

            <div className={styles.checkboxGroup}>
              <label>
                <input
                  type="checkbox"
                  name="dealer_stands_soft"
                  checked={config.dealer_stands_soft}
                  onChange={handleInputChange}
                />
                <span>Dealer stands on soft 17</span>
              </label>

              <label>
                <input
                  type="checkbox"
                  name="allow_splits"
                  checked={config.allow_splits}
                  onChange={handleInputChange}
                />
                <span>Allow splitting</span>
              </label>

              <label>
                <input
                  type="checkbox"
                  name="allow_double_down"
                  checked={config.allow_double_down}
                  onChange={handleInputChange}
                />
                <span>Allow double down</span>
              </label>

              <label>
                <input
                  type="checkbox"
                  name="ace_high"
                  checked={config.ace_high}
                  onChange={handleInputChange}
                />
                <span>Ace counts as 1 or 11</span>
              </label>
            </div>

            <div className={styles.formGroup}>
              <label>Player Strategies</label>
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

            <button type="submit" className={styles.submitButton} disabled={loading || config.players.length === 0}>
              {loading ? 'Running...' : 'Run Simulation'}
            </button>
          </form>
        </aside>

        <main className={styles.main}>
          {loading && <LoadingSpinner message="Running blackjack simulation..." />}
          {error && <ErrorMessage message={error} onRetry={handleSubmit} />}
          {results && (
            <div className={styles.results}>
              <h2>Results</h2>
              <div className={styles.resultsHeader}>
                <div className={styles.stat}>
                  <span className={styles.statLabel}>Total Games</span>
                  <span className={styles.statValue}>{results.total_games.toLocaleString()}</span>
                </div>
                <div className={styles.stat}>
                  <span className={styles.statLabel}>Total Hands</span>
                  <span className={styles.statValue}>{results.total_hands.toLocaleString()}</span>
                </div>
                <div className={styles.stat}>
                  <span className={styles.statLabel}>Dealer Bust Rate</span>
                  <span className={styles.statValue}>{(results.dealer_bust_rate * 100).toFixed(2)}%</span>
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
                      <th>Win Rate</th>
                      <th>ROI</th>
                      <th>Net Profit</th>
                      <th>Games</th>
                      <th>Wins</th>
                      <th>Losses</th>
                      <th>Blackjacks</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.player_stats.map((player) => (
                      <tr key={player.name}>
                        <td className={styles.strategyName}>{player.name}</td>
                        <td className={player.win_rate > 0.5 ? styles.positive : styles.negative}>
                          {(player.win_rate * 100).toFixed(2)}%
                        </td>
                        <td className={player.roi > 0 ? styles.positive : styles.negative}>
                          {player.roi.toFixed(2)}%
                        </td>
                        <td className={player.net_profit >= 0 ? styles.positive : styles.negative}>
                          {player.net_profit >= 0 ? '+' : ''}{player.net_profit.toFixed(2)}
                        </td>
                        <td>{player.games_played.toLocaleString()}</td>
                        <td>{player.wins.toLocaleString()}</td>
                        <td>{player.losses.toLocaleString()}</td>
                        <td>{player.blackjacks.toLocaleString()}</td>
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

export default BlackjackPage;