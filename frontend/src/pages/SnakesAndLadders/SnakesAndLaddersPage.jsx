import { useState } from 'react';
import { GiSnake } from 'react-icons/gi';
import { FaPlay, FaInfoCircle } from 'react-icons/fa';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { snakesAndLaddersApi } from '../../utils/api';
import pageStyles from '../SimulationPage.module.css';
import gameInfo from './snakesAndLadders.json';

const PAGE_COLOR = '#f59e0b';
const CHART_COLORS = ['#f59e0b', '#3b82f6', '#8b5cf6', '#06b6d4', '#ef4444', '#10b981'];

const tooltipStyle = {
  background: 'var(--card-primary)',
  border: '1px solid var(--border)',
  borderRadius: '8px',
  fontSize: '12px',
  padding: '8px 12px',
};

export default function SnakesAndLaddersPage() {
  const [config, setConfig] = useState({
    num_games: 10000,
    num_players: 2,
    board_size: 34,
    num_snakes: 5,
    num_ladders: 5,
    bounce_back: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const [results, setResults] = useState(null);
  const [showInfo, setShowInfo] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setConfig(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : parseInt(value),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); setError(null); setResults(null);
    try {
      const res = await snakesAndLaddersApi.simulate(config);
      setResults(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Simulation failed. Check your settings and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={pageStyles.page} style={{ '--page-accent': PAGE_COLOR }}>

      {/* ── Config Row ── */}
      <section className={pageStyles.configSection}>
        <form onSubmit={handleSubmit} className={pageStyles.configForm}>
          <div className={pageStyles.configInputs}>

            <div className={pageStyles.inputGroup}>
              <label htmlFor="sl-games">Games</label>
              <input id="sl-games" type="number" name="num_games"
                value={config.num_games} onChange={handleChange}
                min="100" max="100000" style={{ width: 90 }} />
            </div>

            <div className={pageStyles.inputGroup}>
              <label htmlFor="sl-players">Players</label>
              <input id="sl-players" type="number" name="num_players"
                value={config.num_players} onChange={handleChange}
                min="2" max="6" style={{ width: 60 }} />
            </div>

            <div className={pageStyles.inputGroup}>
              <label htmlFor="sl-board">Board Size</label>
              <input id="sl-board" type="number" name="board_size"
                value={config.board_size} onChange={handleChange}
                min="20" max="100" style={{ width: 72 }} />
            </div>

            <div className={pageStyles.inputGroup}>
              <label htmlFor="sl-snakes">Snakes</label>
              <input id="sl-snakes" type="number" name="num_snakes"
                value={config.num_snakes} onChange={handleChange}
                min="0" max="20" style={{ width: 60 }} />
            </div>

            <div className={pageStyles.inputGroup}>
              <label htmlFor="sl-ladders">Ladders</label>
              <input id="sl-ladders" type="number" name="num_ladders"
                value={config.num_ladders} onChange={handleChange}
                min="0" max="20" style={{ width: 60 }} />
            </div>

            <div className={pageStyles.toggleGroup}>
              <span>Rules</span>
              <label>
                <input type="checkbox" name="bounce_back"
                  checked={config.bounce_back} onChange={handleChange} />
                Bounce Back
              </label>
            </div>

          </div>
          <div className={pageStyles.configActions}>
            <button type="submit" className={pageStyles.runButton} disabled={loading}>
              <FaPlay size={11} />
              {loading ? 'Running…' : 'Run'}
            </button>
          </div>
        </form>
      </section>

      {/* ── Info Section ── */}
      <section className={pageStyles.infoSection}>
        <button className={pageStyles.infoToggle} onClick={() => setShowInfo(v => !v)}>
          <FaInfoCircle size={13} />
          How Snakes &amp; Ladders works &nbsp;{showInfo ? '▲' : '▼'}
        </button>
        {showInfo && (
          <div className={pageStyles.infoBody}>
            <p className={pageStyles.infoOverview}>{gameInfo.overview}</p>
            <div className={pageStyles.infoGrid}>
              <div className={pageStyles.infoRules}>
                <h4>Rules</h4>
                <ul>{gameInfo.rules.map((r, i) => <li key={i}>{r}</li>)}</ul>
              </div>
              <div className={pageStyles.infoMonte}>
                <h4>Monte Carlo Approach</h4>
                <p>{gameInfo.monteCarloExplanation}</p>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* ── States ── */}
      {loading && (
        <div className={pageStyles.loadingWrap}>
          <div className={pageStyles.spinner} />
        </div>
      )}

      {error && !loading && (
        <div className={pageStyles.errorBanner}>
          <span>{error}</span>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {!results && !loading && !error && (
        <div className={pageStyles.emptyState}>
          <GiSnake />
          <h3>Ready to simulate</h3>
          <p>Configure your board and click Run to analyse probability distributions.</p>
        </div>
      )}

      {/* ── Dashboard ── */}
      {results && !loading && (
        <section className={pageStyles.dashboard}>

          {/* Stat cards */}
          <div className={pageStyles.statRow}>
            <div className={pageStyles.statCard}>
              <span className={pageStyles.statLabel}>Games played</span>
              <span className={pageStyles.statValue}>{results.total_games.toLocaleString()}</span>
            </div>
            <div className={pageStyles.statCard}>
              <span className={pageStyles.statLabel}>Avg game length</span>
              <span className={pageStyles.statValue}>{results.average_game_length.toFixed(1)}</span>
              <span className={pageStyles.statSub}>rolls per game</span>
            </div>
            <div className={pageStyles.statCard}>
              <span className={pageStyles.statLabel}>Shortest game</span>
              <span className={pageStyles.statValue}>{results.shortest_game}</span>
              <span className={pageStyles.statSub}>rolls</span>
            </div>
            <div className={pageStyles.statCard}>
              <span className={pageStyles.statLabel}>Longest game</span>
              <span className={pageStyles.statValue}>{results.longest_game}</span>
              <span className={pageStyles.statSub}>rolls</span>
            </div>
            <div className={pageStyles.statCard}>
              <span className={pageStyles.statLabel}>Run time</span>
              <span className={pageStyles.statValue}>{results.execution_time}s</span>
            </div>
          </div>

          {/* Charts */}
          <div className={pageStyles.chartsGrid}>

            {/* Win rates */}
            <div className={pageStyles.chartCard}>
              <p className={pageStyles.chartTitle}>Win Rate by Player (Turn Order)</p>
              <ResponsiveContainer width="100%" height={230}>
                <BarChart data={results.player_stats} barCategoryGap="35%">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)"
                    opacity={0.6} vertical={false} />
                  <XAxis dataKey="name" stroke="var(--text-muted)"
                    tick={{ fontSize: 11 }} tickLine={false} />
                  <YAxis stroke="var(--text-muted)" tick={{ fontSize: 11 }} tickLine={false}
                    tickFormatter={v => `${(v * 100).toFixed(0)}%`} domain={[0, 1]} />
                  <Tooltip contentStyle={tooltipStyle}
                    formatter={(v) => [`${(v * 100).toFixed(1)}%`, 'Win rate']} />
                  <Bar dataKey="win_rate" radius={[4, 4, 0, 0]}>
                    {results.player_stats.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Avg rolls */}
            <div className={pageStyles.chartCard}>
              <p className={pageStyles.chartTitle}>Average Rolls per Game (per Player)</p>
              <ResponsiveContainer width="100%" height={230}>
                <BarChart data={results.player_stats} barCategoryGap="35%">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)"
                    opacity={0.6} vertical={false} />
                  <XAxis dataKey="name" stroke="var(--text-muted)"
                    tick={{ fontSize: 11 }} tickLine={false} />
                  <YAxis stroke="var(--text-muted)" tick={{ fontSize: 11 }} tickLine={false} />
                  <Tooltip contentStyle={tooltipStyle}
                    formatter={(v) => [v.toFixed(1), 'Avg rolls']} />
                  <Bar dataKey="average_rolls" radius={[4, 4, 0, 0]}>
                    {results.player_stats.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Snakes vs Ladders hit */}
            <div className={pageStyles.chartCard}>
              <p className={pageStyles.chartTitle}>Avg Snakes Hit per Game (per Player)</p>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={results.player_stats} barCategoryGap="35%">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)"
                    opacity={0.6} vertical={false} />
                  <XAxis dataKey="name" stroke="var(--text-muted)"
                    tick={{ fontSize: 11 }} tickLine={false} />
                  <YAxis stroke="var(--text-muted)" tick={{ fontSize: 11 }} tickLine={false} />
                  <Tooltip contentStyle={tooltipStyle}
                    formatter={(v) => [v.toFixed(2), 'Avg snakes hit']} />
                  <Bar dataKey="average_snakes_hit" radius={[4, 4, 0, 0]} fill="#ef4444" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className={pageStyles.chartCard}>
              <p className={pageStyles.chartTitle}>Avg Ladders Climbed per Game (per Player)</p>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={results.player_stats} barCategoryGap="35%">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)"
                    opacity={0.6} vertical={false} />
                  <XAxis dataKey="name" stroke="var(--text-muted)"
                    tick={{ fontSize: 11 }} tickLine={false} />
                  <YAxis stroke="var(--text-muted)" tick={{ fontSize: 11 }} tickLine={false} />
                  <Tooltip contentStyle={tooltipStyle}
                    formatter={(v) => [v.toFixed(2), 'Avg ladders climbed']} />
                  <Bar dataKey="average_ladders_hit" radius={[4, 4, 0, 0]} fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </div>

          </div>

          {/* Detail table */}
          <div className={pageStyles.tableCard}>
            <p className={pageStyles.chartTitle}>Player Statistics Detail</p>
            <table className={pageStyles.table}>
              <thead>
                <tr>
                  <th>Player</th>
                  <th>Wins</th>
                  <th>Win Rate</th>
                  <th>Avg Rolls</th>
                  <th>Min Rolls</th>
                  <th>Max Rolls</th>
                  <th>Avg Snakes</th>
                  <th>Avg Ladders</th>
                </tr>
              </thead>
              <tbody>
                {results.player_stats.map((p, i) => (
                  <tr key={p.name}>
                    <td>
                      <span className={pageStyles.colorDot}
                        style={{ background: CHART_COLORS[i % CHART_COLORS.length] }} />
                      {p.name}
                    </td>
                    <td>{p.wins.toLocaleString()}</td>
                    <td>{(p.win_rate * 100).toFixed(1)}%</td>
                    <td>{p.average_rolls.toFixed(1)}</td>
                    <td>{p.min_rolls}</td>
                    <td>{p.max_rolls}</td>
                    <td style={{ color: '#ef4444' }}>{p.average_snakes_hit.toFixed(2)}</td>
                    <td style={{ color: '#10b981' }}>{p.average_ladders_hit.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

        </section>
      )}
    </div>
  );
}
