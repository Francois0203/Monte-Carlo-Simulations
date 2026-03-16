import { useState } from 'react';
import { GiCardRandom } from 'react-icons/gi';
import { FaPlay, FaInfoCircle } from 'react-icons/fa';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, ScatterChart, Scatter,
} from 'recharts';
import { pokerApi } from '../../utils/api';
import pageStyles from '../SimulationPage.module.css';
import gameInfo from './poker.json';

const PAGE_COLOR = '#8b5cf6';
const CHART_COLORS = ['#8b5cf6', '#3b82f6', '#06b6d4', '#f59e0b', '#ef4444', '#10b981', '#f97316', '#ec4899'];

const STRATEGIES = [
  { value: 'calling_station',   label: 'Calling Station' },
  { value: 'tight_passive',     label: 'Tight Passive' },
  { value: 'tight_aggressive',  label: 'Tight Aggressive' },
  { value: 'loose_aggressive',  label: 'Loose Aggressive' },
  { value: 'pot_odds_player',   label: 'Pot Odds' },
  { value: 'bluffer',           label: 'Bluffer' },
  { value: 'position_aware',    label: 'Position Aware' },
  { value: 'gto_balanced',      label: 'GTO Balanced' },
];

const tooltipStyle = {
  background: 'var(--card-primary)',
  border: '1px solid var(--border)',
  borderRadius: '8px',
  fontSize: '12px',
  padding: '8px 12px',
};

export default function PokerPage() {
  const [config, setConfig] = useState({
    num_hands: 10000,
    num_players: 4,
    small_blind: 1,
    big_blind: 2,
    starting_stack: 200,
    allow_rebuys: true,
    players: ['tight_aggressive', 'loose_aggressive', 'tight_passive', 'calling_station'],
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

  const toggleStrategy = (val) => {
    setConfig(prev => {
      const next = prev.players.includes(val)
        ? prev.players.filter(s => s !== val)
        : [...prev.players, val];
      return { ...prev, players: next, num_players: next.length };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (config.players.length < 2) return;
    setLoading(true); setError(null); setResults(null);
    try {
      const res = await pokerApi.simulate(config);
      setResults(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Simulation failed. Check your settings and try again.');
    } finally {
      setLoading(false);
    }
  };

  const dol = (v) => `$${Number(v).toFixed(0)}`;
  const pct = (v) => `${(v * 100).toFixed(1)}%`;
  const best = results?.player_stats?.reduce((b, p) => p.net_profit > b.net_profit ? p : b, results.player_stats[0]);

  return (
    <div className={pageStyles.page} style={{ '--page-accent': PAGE_COLOR }}>

      {/* ── Config Row ── */}
      <section className={pageStyles.configSection}>
        <form onSubmit={handleSubmit} className={pageStyles.configForm}>
          <div className={pageStyles.configInputs}>

            <div className={pageStyles.inputGroup}>
              <label htmlFor="pk-hands">Hands</label>
              <input id="pk-hands" type="number" name="num_hands"
                value={config.num_hands} onChange={handleChange}
                min="100" max="100000" style={{ width: 90 }} />
            </div>

            <div className={pageStyles.inputGroup}>
              <label htmlFor="pk-sb">Small Blind</label>
              <input id="pk-sb" type="number" name="small_blind"
                value={config.small_blind} onChange={handleChange}
                min="1" max="100" style={{ width: 72 }} />
            </div>

            <div className={pageStyles.inputGroup}>
              <label htmlFor="pk-bb">Big Blind</label>
              <input id="pk-bb" type="number" name="big_blind"
                value={config.big_blind} onChange={handleChange}
                min="2" max="200" style={{ width: 72 }} />
            </div>

            <div className={pageStyles.inputGroup}>
              <label htmlFor="pk-stack">Starting Stack</label>
              <input id="pk-stack" type="number" name="starting_stack"
                value={config.starting_stack} onChange={handleChange}
                min="50" max="10000" style={{ width: 84 }} />
            </div>

            <div className={pageStyles.toggleGroup}>
              <span>Options</span>
              <label>
                <input type="checkbox" name="allow_rebuys"
                  checked={config.allow_rebuys} onChange={handleChange} />
                Allow Rebuys
              </label>
            </div>

            <div className={pageStyles.chipGroup}>
              <span className={pageStyles.chipGroupLabel}>
                Players ({config.players.length}/9)
              </span>
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
              disabled={loading || config.players.length < 2}>
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
          How Texas Hold'em works &nbsp;{showInfo ? '▲' : '▼'}
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
          <GiCardRandom />
          <h3>Ready to simulate</h3>
          <p>Select at least 2 player strategies and click Run to start.</p>
        </div>
      )}

      {/* ── Dashboard ── */}
      {results && !loading && (
        <section className={pageStyles.dashboard}>

          {/* Stat cards */}
          <div className={pageStyles.statRow}>
            <div className={pageStyles.statCard}>
              <span className={pageStyles.statLabel}>Hands played</span>
              <span className={pageStyles.statValue}>{results.total_hands.toLocaleString()}</span>
            </div>
            <div className={pageStyles.statCard}>
              <span className={pageStyles.statLabel}>Avg pot size</span>
              <span className={pageStyles.statValue}>{dol(results.average_pot_size)}</span>
              <span className={pageStyles.statSub}>{results.total_pots.toLocaleString()} pots</span>
            </div>
            {best && (
              <div className={pageStyles.statCard}>
                <span className={pageStyles.statLabel}>Top earner</span>
                <span className={pageStyles.statValue}
                  style={{ fontSize: '1.125rem', color: '#10b981' }}>
                  {best.name}
                </span>
                <span className={pageStyles.statSub}>{dol(best.net_profit)} net profit</span>
              </div>
            )}
            <div className={pageStyles.statCard}>
              <span className={pageStyles.statLabel}>Run time</span>
              <span className={pageStyles.statValue}>{results.execution_time}s</span>
            </div>
          </div>

          {/* Charts */}
          <div className={pageStyles.chartsGrid}>

            {/* Net profit */}
            <div className={pageStyles.chartCard}>
              <p className={pageStyles.chartTitle}>Net Profit by Strategy</p>
              <ResponsiveContainer width="100%" height={230}>
                <BarChart data={results.player_stats} layout="vertical" barCategoryGap="30%">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)"
                    opacity={0.6} horizontal={false} />
                  <XAxis type="number" stroke="var(--text-muted)"
                    tick={{ fontSize: 11 }} tickLine={false}
                    tickFormatter={v => `$${v}`} />
                  <YAxis type="category" dataKey="name" stroke="var(--text-muted)"
                    tick={{ fontSize: 11 }} tickLine={false} width={110} />
                  <Tooltip contentStyle={tooltipStyle}
                    formatter={(v) => [dol(v), 'Net profit']} />
                  <Bar dataKey="net_profit" radius={[0, 4, 4, 0]}>
                    {results.player_stats.map((p, i) => (
                      <Cell key={i}
                        fill={p.net_profit >= 0
                          ? CHART_COLORS[i % CHART_COLORS.length]
                          : '#ef4444'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Win rate */}
            <div className={pageStyles.chartCard}>
              <p className={pageStyles.chartTitle}>Win Rate by Strategy</p>
              <ResponsiveContainer width="100%" height={230}>
                <BarChart data={results.player_stats} layout="vertical" barCategoryGap="30%">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)"
                    opacity={0.6} horizontal={false} />
                  <XAxis type="number" stroke="var(--text-muted)"
                    tick={{ fontSize: 11 }} tickLine={false}
                    tickFormatter={v => `${(v * 100).toFixed(0)}%`} domain={[0, 1]} />
                  <YAxis type="category" dataKey="name" stroke="var(--text-muted)"
                    tick={{ fontSize: 11 }} tickLine={false} width={110} />
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

            {/* VPIP comparison */}
            <div className={pageStyles.chartCard}>
              <p className={pageStyles.chartTitle}>VPIP (Voluntary Money In Pot)</p>
              <ResponsiveContainer width="100%" height={230}>
                <BarChart data={results.player_stats} layout="vertical" barCategoryGap="30%">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)"
                    opacity={0.6} horizontal={false} />
                  <XAxis type="number" stroke="var(--text-muted)"
                    tick={{ fontSize: 11 }} tickLine={false}
                    tickFormatter={v => `${(v * 100).toFixed(0)}%`} domain={[0, 1]} />
                  <YAxis type="category" dataKey="name" stroke="var(--text-muted)"
                    tick={{ fontSize: 11 }} tickLine={false} width={110} />
                  <Tooltip contentStyle={tooltipStyle}
                    formatter={(v) => [pct(v), 'VPIP']} />
                  <Bar dataKey="vpip" radius={[0, 4, 4, 0]}>
                    {results.player_stats.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Biggest pots */}
            <div className={pageStyles.chartCard}>
              <p className={pageStyles.chartTitle}>Biggest Pot Won per Strategy</p>
              <ResponsiveContainer width="100%" height={230}>
                <BarChart data={results.player_stats} layout="vertical" barCategoryGap="30%">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)"
                    opacity={0.6} horizontal={false} />
                  <XAxis type="number" stroke="var(--text-muted)"
                    tick={{ fontSize: 11 }} tickLine={false}
                    tickFormatter={v => `$${v}`} />
                  <YAxis type="category" dataKey="name" stroke="var(--text-muted)"
                    tick={{ fontSize: 11 }} tickLine={false} width={110} />
                  <Tooltip contentStyle={tooltipStyle}
                    formatter={(v) => [dol(v), 'Biggest pot']} />
                  <Bar dataKey="biggest_pot" radius={[0, 4, 4, 0]}>
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
                  <th>Hands Won</th>
                  <th>Win Rate</th>
                  <th>Net Profit</th>
                  <th>VPIP</th>
                  <th>Avg Pot Won</th>
                  <th>Biggest Pot</th>
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
                    <td>{p.hands_won.toLocaleString()}</td>
                    <td>{pct(p.win_rate)}</td>
                    <td className={p.net_profit >= 0 ? pageStyles.positive : pageStyles.negative}>
                      {dol(p.net_profit)}
                    </td>
                    <td>{pct(p.vpip)}</td>
                    <td>{dol(p.avg_pot_won)}</td>
                    <td>{dol(p.biggest_pot)}</td>
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
