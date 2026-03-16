import { useState } from 'react';
import { GiCardJoker } from 'react-icons/gi';
import { FaPlay, FaInfoCircle } from 'react-icons/fa';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Cell, Legend,
} from 'recharts';
import { blackjackApi } from '../../utils/api';
import pageStyles from '../SimulationPage.module.css';
import gameInfo from './blackjack.json';

const PAGE_COLOR = '#3b82f6';
const CHART_COLORS = ['#3b82f6', '#8b5cf6', '#06b6d4', '#f59e0b', '#ef4444', '#10b981', '#f97316', '#ec4899'];

const STRATEGIES = [
  { value: 'never_bust',    label: 'Never Bust' },
  { value: 'safe',          label: 'Safe' },
  { value: 'basic',         label: 'Basic Strategy' },
  { value: 'aggressive',    label: 'Aggressive' },
  { value: 'mimic_dealer',  label: 'Mimic Dealer' },
  { value: 'gut_feel',      label: 'Gut Feel' },
  { value: 'card_counter',  label: 'Card Counter' },
  { value: 'martingale',    label: 'Martingale' },
];

const tooltipStyle = {
  background: 'var(--card-primary)',
  border: '1px solid var(--border)',
  borderRadius: '8px',
  fontSize: '12px',
  padding: '8px 12px',
};

export default function BlackjackPage() {
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
  const [error, setError]     = useState(null);
  const [results, setResults] = useState(null);
  const [showInfo, setShowInfo] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setConfig(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : type === 'number' ? parseFloat(value) : value,
    }));
  };

  const toggleStrategy = (val) => {
    setConfig(prev => ({
      ...prev,
      players: prev.players.includes(val)
        ? prev.players.filter(s => s !== val)
        : [...prev.players, val],
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!config.players.length) return;
    setLoading(true); setError(null); setResults(null);
    try {
      const res = await blackjackApi.simulate(config);
      setResults(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Simulation failed. Check your settings and try again.');
    } finally {
      setLoading(false);
    }
  };

  const pct  = (v) => `${(v * 100).toFixed(1)}%`;
  const dol  = (v) => `$${Number(v).toFixed(0)}`;
  const best = results?.player_stats?.reduce((b, p) => p.roi > b.roi ? p : b, results.player_stats[0]);

  return (
    <div className={pageStyles.page} style={{ '--page-accent': PAGE_COLOR }}>

      {/* ── Config Row ── */}
      <section className={pageStyles.configSection}>
        <form onSubmit={handleSubmit} className={pageStyles.configForm}>
          <div className={pageStyles.configInputs}>

            <div className={pageStyles.inputGroup}>
              <label htmlFor="bj-games">Games</label>
              <input id="bj-games" type="number" name="num_games"
                value={config.num_games} onChange={handleChange}
                min="100" max="100000" style={{ width: 90 }} />
            </div>

            <div className={pageStyles.inputGroup}>
              <label htmlFor="bj-decks">Decks</label>
              <input id="bj-decks" type="number" name="num_decks"
                value={config.num_decks} onChange={handleChange}
                min="1" max="8" style={{ width: 60 }} />
            </div>

            <div className={pageStyles.inputGroup}>
              <label htmlFor="bj-payout">BJ Payout</label>
              <input id="bj-payout" type="number" name="blackjack_payout"
                value={config.blackjack_payout} onChange={handleChange}
                min="1.0" max="2.0" step="0.1" style={{ width: 72 }} />
            </div>

            <div className={pageStyles.toggleGroup}>
              <span>House Rules</span>
              <label>
                <input type="checkbox" name="dealer_stands_soft"
                  checked={config.dealer_stands_soft} onChange={handleChange} />
                Soft 17
              </label>
              <label>
                <input type="checkbox" name="allow_splits"
                  checked={config.allow_splits} onChange={handleChange} />
                Splits
              </label>
              <label>
                <input type="checkbox" name="allow_double_down"
                  checked={config.allow_double_down} onChange={handleChange} />
                Double Down
              </label>
            </div>

            <div className={pageStyles.chipGroup}>
              <span className={pageStyles.chipGroupLabel}>Strategies ({config.players.length})</span>
              <div className={pageStyles.chips}>
                {STRATEGIES.map(s => (
                  <button key={s.value} type="button"
                    className={`${pageStyles.chip} ${config.players.includes(s.value) ? pageStyles.chipActive : ''}`}
                    onClick={() => toggleStrategy(s.value)}>
                    {s.label}
                  </button>
                ))}
              </div>
            </div>

          </div>
          <div className={pageStyles.configActions}>
            <button type="submit" className={pageStyles.runButton}
              disabled={loading || !config.players.length}>
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
          How Blackjack works &nbsp;{showInfo ? '▲' : '▼'}
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
          <GiCardJoker />
          <h3>Ready to simulate</h3>
          <p>Choose your strategies and click Run to start the Monte Carlo simulation.</p>
        </div>
      )}

      {/* ── Dashboard ── */}
      {results && !loading && (
        <section className={pageStyles.dashboard}>

          {/* Stat cards */}
          <div className={pageStyles.statRow}>
            <div className={pageStyles.statCard}>
              <span className={pageStyles.statLabel}>Games simulated</span>
              <span className={pageStyles.statValue}>{results.total_games.toLocaleString()}</span>
              <span className={pageStyles.statSub}>{results.total_hands.toLocaleString()} hands</span>
            </div>
            <div className={pageStyles.statCard}>
              <span className={pageStyles.statLabel}>Dealer bust rate</span>
              <span className={pageStyles.statValue}>{pct(results.dealer_bust_rate)}</span>
              <span className={pageStyles.statSub}>{results.dealer_busts.toLocaleString()} busts</span>
            </div>
            {best && (
              <div className={pageStyles.statCard}>
                <span className={pageStyles.statLabel}>Best ROI</span>
                <span className={pageStyles.statValue}
                  style={{ color: best.roi >= 0 ? '#10b981' : '#ef4444' }}>
                  {best.roi}%
                </span>
                <span className={pageStyles.statSub}>{best.name}</span>
              </div>
            )}
            <div className={pageStyles.statCard}>
              <span className={pageStyles.statLabel}>Run time</span>
              <span className={pageStyles.statValue}>{results.execution_time}s</span>
              <span className={pageStyles.statSub}>
                {Math.round(results.total_games / results.execution_time).toLocaleString()} games/s
              </span>
            </div>
          </div>

          {/* Charts */}
          <div className={pageStyles.chartsGrid}>

            {/* Profit over time */}
            {results.chart_data?.length > 0 && (
              <div className={pageStyles.chartCard} style={{ gridColumn: '1 / -1' }}>
                <p className={pageStyles.chartTitle}>Cumulative Profit Over Time</p>
                <ResponsiveContainer width="100%" height={260}>
                  <LineChart data={results.chart_data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.6} />
                    <XAxis dataKey="game" stroke="var(--text-muted)"
                      tick={{ fontSize: 11 }} tickLine={false} />
                    <YAxis stroke="var(--text-muted)" tick={{ fontSize: 11 }} tickLine={false}
                      tickFormatter={v => `$${v}`} />
                    <Tooltip contentStyle={tooltipStyle}
                      formatter={(v, name) => [dol(v), name]} />
                    <Legend iconType="circle" iconSize={8}
                      wrapperStyle={{ fontSize: 12 }} />
                    {results.player_stats.map((p, i) => (
                      <Line key={p.name} type="monotone" dataKey={p.name}
                        stroke={CHART_COLORS[i % CHART_COLORS.length]}
                        strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* ROI comparison */}
            <div className={pageStyles.chartCard}>
              <p className={pageStyles.chartTitle}>ROI by Strategy</p>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={results.player_stats} layout="vertical" barCategoryGap="30%">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)"
                    opacity={0.6} horizontal={false} />
                  <XAxis type="number" stroke="var(--text-muted)"
                    tick={{ fontSize: 11 }} tickLine={false} unit="%" />
                  <YAxis type="category" dataKey="name" stroke="var(--text-muted)"
                    tick={{ fontSize: 11 }} tickLine={false} width={95} />
                  <Tooltip contentStyle={tooltipStyle}
                    formatter={(v) => [`${v}%`, 'ROI']} />
                  <Bar dataKey="roi" radius={[0, 4, 4, 0]}>
                    {results.player_stats.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Win-rate comparison */}
            <div className={pageStyles.chartCard}>
              <p className={pageStyles.chartTitle}>Win Rate by Strategy</p>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={results.player_stats} layout="vertical" barCategoryGap="30%">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)"
                    opacity={0.6} horizontal={false} />
                  <XAxis type="number" stroke="var(--text-muted)"
                    tick={{ fontSize: 11 }} tickLine={false}
                    tickFormatter={v => `${(v * 100).toFixed(0)}%`} domain={[0, 1]} />
                  <YAxis type="category" dataKey="name" stroke="var(--text-muted)"
                    tick={{ fontSize: 11 }} tickLine={false} width={95} />
                  <Tooltip contentStyle={tooltipStyle}
                    formatter={(v) => [pct(v), 'Win rate']} />
                  <Bar dataKey="win_rate" radius={[0, 4, 4, 0]}>
                    {results.player_stats.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

          </div>

          {/* Detail table */}
          <div className={pageStyles.tableCard}>
            <p className={pageStyles.chartTitle}>Strategy Performance Detail</p>
            <table className={pageStyles.table}>
              <thead>
                <tr>
                  <th>Strategy</th>
                  <th>Win Rate</th>
                  <th>Net Profit</th>
                  <th>ROI</th>
                  <th>Blackjacks</th>
                  <th>Busts</th>
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
                    <td>{pct(p.win_rate)}</td>
                    <td className={p.net_profit >= 0 ? pageStyles.positive : pageStyles.negative}>
                      {dol(p.net_profit)}
                    </td>
                    <td className={p.roi >= 0 ? pageStyles.positive : pageStyles.negative}>
                      {p.roi}%
                    </td>
                    <td>{p.blackjacks?.toLocaleString() ?? '—'}</td>
                    <td>{p.busts?.toLocaleString() ?? '—'}</td>
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
