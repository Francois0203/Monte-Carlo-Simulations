import { useState } from 'react';
import { naughtsAndCrossesApi } from '../../utils/api';
import LoadingSpinner from '../../components/LoadingSpinner/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage/ErrorMessage';
import styles from '../Blackjack/BlackjackPage.module.css';

const NaughtsAndCrossesPage = () => {
  const [config, setConfig] = useState({
    num_games: 10000,
    num_players: 2,
    board_size: 3,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setConfig((prev) => ({
      ...prev,
      [name]: parseInt(value),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await naughtsAndCrossesApi.simulate(config);
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
        <h1>⭕ Tic-Tac-Toe Simulation</h1>
        <p>Explore random play outcomes in Naughts and Crosses</p>
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
              <label htmlFor="board_size">Board Size</label>
              <select
                id="board_size"
                name="board_size"
                value={config.board_size}
                onChange={handleInputChange}
              >
                <option value={3}>3x3 (Classic)</option>
                <option value={4}>4x4</option>
                <option value={5}>5x5</option>
              </select>
            </div>

            <button type="submit" className={styles.submitButton} disabled={loading}>
              {loading ? 'Running...' : 'Run Simulation'}
            </button>
          </form>
        </aside>

        <main className={styles.main}>
          {loading && <LoadingSpinner message="Running Tic-Tac-Toe simulation..." />}
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
                  <span className={styles.statLabel}>X Wins</span>
                  <span className={styles.statValue}>{results.total_wins_x.toLocaleString()}</span>
                </div>
                <div className={styles.stat}>
                  <span className={styles.statLabel}>O Wins</span>
                  <span className={styles.statValue}>{results.total_wins_o.toLocaleString()}</span>
                </div>
                <div className={styles.stat}>
                  <span className={styles.statLabel}>Draws</span>
                  <span className={styles.statValue}>{results.total_draws.toLocaleString()}</span>
                </div>
              </div>

              <div className={styles.playersTable}>
                <table>
                  <thead>
                    <tr>
                      <th>Player</th>
                      <th>Symbol</th>
                      <th>Wins</th>
                      <th>Losses</th>
                      <th>Draws</th>
                      <th>Win Rate</th>
                      <th>Loss Rate</th>
                      <th>Draw Rate</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.player_stats.map((player) => (
                      <tr key={player.name}>
                        <td className={styles.strategyName}>{player.name}</td>
                        <td>{player.symbol}</td>
                        <td>{player.wins.toLocaleString()}</td>
                        <td>{player.losses.toLocaleString()}</td>
                        <td>{player.draws.toLocaleString()}</td>
                        <td className={styles.positive}>{(player.win_rate * 100).toFixed(2)}%</td>
                        <td className={styles.negative}>{(player.loss_rate * 100).toFixed(2)}%</td>
                        <td>{(player.draw_rate * 100).toFixed(2)}%</td>
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

export default NaughtsAndCrossesPage;
