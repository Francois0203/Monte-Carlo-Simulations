import { useState } from 'react';
import { GiTicTacToe } from 'react-icons/gi';
import { FaPlay, FaInfoCircle } from 'react-icons/fa';
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from 'recharts';
import { ticTacToeApi } from '../../utils/api';
import pageStyles from '../SimulationPage.module.css';
import gameInfo from './ticTacToe.json';

const PAGE_COLOR = '#06b6d4';
const PIE_COLORS = ['#06b6d4', '#8b5cf6', '#64748b'];

const tooltipStyle = {
  background: 'var(--card-primary)',
  border: '1px solid var(--border)',
  borderRadius: '8px',
  fontSize: '12px',
  padding: '8px 12px',
};

export default function TicTacToePage() {
  const [config, setConfig] = useState({
    num_games: 10000,
    num_players: 2,
    board_size: 3,
  });
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);
  const [results, setResults]   = useState(null);
  const [showInfo, setShowInfo] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setConfig(prev => ({ ...prev, [name]: parseInt(value) }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); setError(null); setResults(null);
    try {
      const res = await ticTacToeApi.simulate(config);
      setResults(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Simulation failed. Check your settings and try again.');
    } finally {
      setLoading(false);
    }
  };

  const pct = (v) => `${(v * 100).toFixed(1)}%`;

  const pieData = results
    ? [
        { name: 'X Wins', value: results.total_wins_x },
        { name: 'O Wins', value: results.total_wins_o },
        { name: 'Draws',  value: results.total_draws  },
      ]
    : [];

  const barData = results?.player_stats?.map(p => ({
    name: `${p.name} (${p.symbol})`,
    win_rate:  p.win_rate,
    draw_rate: p.draw_rate,
    loss_rate: p.loss_rate,
  })) ?? [];

  return (
    <div className={pageStyles.page} style={{ '--page-accent': PAGE_COLOR }}>

      {/* ── Config Row ── */}
      <section className={pageStyles.configSection}>
        <form onSubmit={handleSubmit} className={pageStyles.configForm}>
          <div className={pageStyles.configInputs}>

            <div className={pageStyles.inputGroup}>
              <label htmlFor="ttt-games">Games</label>
              <input id="ttt-games" type="number" name="num_games"
                value={config.num_games} onChange={handleChange}
                min="100" max="100000" style={{ width: 90 }} />
            </div>

            <div className={pageStyles.inputGroup}>
              <label htmlFor="ttt-board">Board Size</label>
              <select id="ttt-board" name="board_size"
                value={config.board_size} onChange={handleChange}
                style={{ width: 90 }}>
                <option value={3}>3 × 3</option>
                <option value={4}>4 × 4</option>
                <option value={5}>5 × 5</option>
              </select>
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
          How Tic-Tac-Toe works &nbsp;{showInfo ? '▲' : '▼'}
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
          <GiTicTacToe />
          <h3>Ready to simulate</h3>
          <p>Choose a board size and click Run to explore outcome distributions.</p>
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
              <span className={pageStyles.statLabel}>X wins</span>
              <span className={pageStyles.statValue}
                style={{ color: PIE_COLORS[0] }}>
                {(results.total_wins_x / results.total_games * 100).toFixed(1)}%
              </span>
              <span className={pageStyles.statSub}>{results.total_wins_x.toLocaleString()} games</span>
            </div>
            <div className={pageStyles.statCard}>
              <span className={pageStyles.statLabel}>O wins</span>
              <span className={pageStyles.statValue}
                style={{ color: PIE_COLORS[1] }}>
                {(results.total_wins_o / results.total_games * 100).toFixed(1)}%
              </span>
              <span className={pageStyles.statSub}>{results.total_wins_o.toLocaleString()} games</span>
            </div>
            <div className={pageStyles.statCard}>
              <span className={pageStyles.statLabel}>Draw rate</span>
              <span className={pageStyles.statValue}
                style={{ color: PIE_COLORS[2] }}>
                {pct(results.draw_rate)}
              </span>
              <span className={pageStyles.statSub}>{results.total_draws.toLocaleString()} draws</span>
            </div>
            <div className={pageStyles.statCard}>
              <span className={pageStyles.statLabel}>Avg moves</span>
              <span className={pageStyles.statValue}>
                {results.average_moves_per_game.toFixed(1)}
              </span>
              <span className={pageStyles.statSub}>per game</span>
            </div>
            <div className={pageStyles.statCard}>
              <span className={pageStyles.statLabel}>Run time</span>
              <span className={pageStyles.statValue}>{results.execution_time}s</span>
            </div>
          </div>

          {/* Charts */}
          <div className={pageStyles.chartsGrid}>

            {/* Outcome pie */}
            <div className={pageStyles.chartCard}>
              <p className={pageStyles.chartTitle}>Outcome Distribution</p>
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="48%"
                    innerRadius={55}
                    outerRadius={90}
                    paddingAngle={3}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                    labelLine={false}
                  >
                    {pieData.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={tooltipStyle}
                    formatter={(v, name) => [v.toLocaleString(), name]} />
                  <Legend iconType="circle" iconSize={8}
                    wrapperStyle={{ fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Win/draw/loss rates stacked bar */}
            <div className={pageStyles.chartCard}>
              <p className={pageStyles.chartTitle}>Win / Draw / Loss Rates per Player</p>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={barData} barCategoryGap="40%">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)"
                    opacity={0.6} vertical={false} />
                  <XAxis dataKey="name" stroke="var(--text-muted)"
                    tick={{ fontSize: 11 }} tickLine={false} />
                  <YAxis stroke="var(--text-muted)" tick={{ fontSize: 11 }} tickLine={false}
                    tickFormatter={v => `${(v * 100).toFixed(0)}%`} domain={[0, 1]} />
                  <Tooltip contentStyle={tooltipStyle}
                    formatter={(v, name) => [pct(v), name]} />
                  <Legend iconType="circle" iconSize={8}
                    wrapperStyle={{ fontSize: 12 }} />
                  <Bar dataKey="win_rate"  stackId="a" fill={PIE_COLORS[0]} name="Win"  radius={[0, 0, 0, 0]} />
                  <Bar dataKey="draw_rate" stackId="a" fill={PIE_COLORS[2]} name="Draw" />
                  <Bar dataKey="loss_rate" stackId="a" fill="#ef4444"        name="Loss" radius={[4, 4, 0, 0]} />
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
                  <th>Symbol</th>
                  <th>Wins</th>
                  <th>Win Rate</th>
                  <th>Draws</th>
                  <th>Draw Rate</th>
                  <th>Losses</th>
                  <th>Loss Rate</th>
                </tr>
              </thead>
              <tbody>
                {results.player_stats.map((p, i) => (
                  <tr key={p.name}>
                    <td>
                      <span className={pageStyles.colorDot}
                        style={{ background: PIE_COLORS[i % PIE_COLORS.length] }} />
                      {p.name}
                    </td>
                    <td><strong>{p.symbol}</strong></td>
                    <td>{p.wins.toLocaleString()}</td>
                    <td className={pageStyles.positive}>{pct(p.win_rate)}</td>
                    <td>{p.draws.toLocaleString()}</td>
                    <td>{pct(p.draw_rate)}</td>
                    <td>{p.losses.toLocaleString()}</td>
                    <td className={pageStyles.negative}>{pct(p.loss_rate)}</td>
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
