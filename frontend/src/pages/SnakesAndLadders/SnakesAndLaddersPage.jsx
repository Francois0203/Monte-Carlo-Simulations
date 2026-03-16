import { useState } from 'react';
import { snakesAndLaddersApi } from '../../utils/api';
import LoadingSpinner from '../../components/LoadingSpinner/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage/ErrorMessage';
import styles from '../Blackjack/BlackjackPage.module.css';

const SnakesAndLaddersPage = () => {
  const [config, setConfig] = useState({
    num_games: 10000,
    num_players: 2,
    board_size: 34,
    num_snakes: 5,
    num_ladders: 5,
    bounce_back: true,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setConfig((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : parseInt(value),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await snakesAndLaddersApi.simulate(config);
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
        <h1>🎲 Snakes & Ladders Simulation</h1>
        <p>Analyze probabilities in this classic board game</p>
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
              <label htmlFor="num_players">Number of Players</label>
              <input
                type="number"
                id="num_players"
                name="num_players"
                value={config.num_players}
                onChange={handleInputChange}
                min="2"
                max="6"
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="board_size">Board Size</label>
              <input
                type="number"
                id="board_size"
                name="board_size"
                value={config.board_size}
                onChange={handleInputChange}
                min="20"
                max="100"
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="num_snakes">Number of Snakes</label>
              <input
                type="number"
                id="num_snakes"
                name="num_snakes"
                value={config.num_snakes}
                onChange={handleInputChange}
                min="0"
                max="20"
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="num_ladders">Number of Ladders</label>
              <input
                type="number"
                id="num_ladders"
                name="num_ladders"
                value={config.num_ladders}
                onChange={handleInputChange}
                min="0"
                max="20"
                required
              />
            </div>

            <div className={styles.checkboxGroup}>
              <label>
                <input
                  type="checkbox"
                  name="bounce_back"
                  checked={config.bounce_back}
                  onChange={handleInputChange}
                />
                <span>Bounce back when overshooting</span>
              </label>
            </div>

            <button type="submit" className={styles.submitButton} disabled={loading}>
              {loading ? 'Running...' : 'Run Simulation'}
            </button>
          </form>
        </aside>

        <main className={styles.main}>
          {loading && <LoadingSpinner message="Running Snakes & Ladders simulation..." />}
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
                  <span className={styles.statLabel}>Avg Game Length</span>
                  <span className={styles.statValue}>{results.average_game_length}</span>
                </div>
                <div className={styles.stat}>
                  <span className={styles.statLabel}>Shortest Game</span>
                  <span className={styles.statValue}>{results.shortest_game}</span>
                </div>
                <div className={styles.stat}>
                  <span className={styles.statLabel}>Longest Game</span>
                  <span className={styles.statValue}>{results.longest_game}</span>
                </div>
              </div>

              <div className={styles.playersTable}>
                <table>
                  <thead>
                    <tr>
                      <th>Player</th>
                      <th>Wins</th>
                      <th>Win Rate</th>
                      <th>Avg Rolls</th>
                      <th>Min Rolls</th>
                      <th>Max Rolls</th>
                      <th>Avg Snakes Hit</th>
                      <th>Avg Ladders Hit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.player_stats.map((player) => (
                      <tr key={player.name}>
                        <td className={styles.strategyName}>{player.name}</td>
                        <td>{player.wins.toLocaleString()}</td>
                        <td>{(player.win_rate * 100).toFixed(2)}%</td>
                        <td>{player.average_rolls}</td>
                        <td>{player.min_rolls}</td>
                        <td>{player.max_rolls}</td>
                        <td>{player.average_snakes_hit}</td>
                        <td>{player.average_ladders_hit}</td>
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

export default SnakesAndLaddersPage;
