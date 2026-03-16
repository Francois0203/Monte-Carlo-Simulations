import { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FaBars, FaTimes, FaHome } from 'react-icons/fa';
import { GiCardJoker, GiCardRandom, GiSnake, GiTicTacToe } from 'react-icons/gi';
import ThemeSwitch from '../ThemeSwitch';
import styles from './NavigationBar.module.css';

const ROUTES = [
  { path: '/', label: 'Home', icon: FaHome, color: 'var(--accent-1)' },
  { path: '/blackjack', label: 'Blackjack', icon: GiCardJoker, color: '#3b82f6' },
  { path: '/poker', label: 'Poker', icon: GiCardRandom, color: '#8b5cf6' },
  { path: '/snakes-and-ladders', label: 'Snakes & Ladders', icon: GiSnake, color: '#f59e0b' },
  { path: '/naughts-and-crosses', label: 'Tic-Tac-Toe', icon: GiTicTacToe, color: '#06b6d4' },
];

export default function NavigationBar({ theme, toggleTheme }) {
  const [open, setOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const dropdownRef = useRef(null);
  const btnRef = useRef(null);

  const current = ROUTES.find(r => r.path === location.pathname) || ROUTES[0];
  const CurrentIcon = current.icon;

  // Close on outside click
  useEffect(() => {
    const handler = (e) => {
      if (
        dropdownRef.current && !dropdownRef.current.contains(e.target) &&
        btnRef.current && !btnRef.current.contains(e.target)
      ) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // Close on Escape
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') setOpen(false); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, []);

  // Close on route change
  useEffect(() => { setOpen(false); }, [location.pathname]);

  const go = (path) => { navigate(path); setOpen(false); };

  return (
    <header className={styles.topBar}>
      {/* Left: menu button + page title */}
      <div className={styles.left}>
        <button
          ref={btnRef}
          className={`${styles.menuBtn} ${open ? styles.menuBtnOpen : ''}`}
          onClick={() => setOpen(v => !v)}
          aria-label={open ? 'Close menu' : 'Open menu'}
          aria-expanded={open}
        >
          {open ? <FaTimes size={16} /> : <FaBars size={16} />}
        </button>

        <div className={styles.divider} />

        <div className={styles.pageLabel} style={{ '--route-color': current.color }}>
          <CurrentIcon className={styles.pageIcon} />
          <div className={styles.pageLabelText}>
            <span className={styles.pageName}>{current.label}</span>
            <span className={styles.pageSub}>Monte Carlo</span>
          </div>
        </div>
      </div>

      {/* Right: theme switch */}
      <div className={styles.right}>
        <ThemeSwitch theme={theme} toggleTheme={toggleTheme} />
      </div>

      {/* Dropdown nav panel */}
      {open && (
        <nav
          ref={dropdownRef}
          className={styles.dropdown}
          aria-label="Site navigation"
        >
          {ROUTES.map(route => {
            const Icon = route.icon;
            const isActive = location.pathname === route.path;
            return (
              <button
                key={route.path}
                className={`${styles.navLink} ${isActive ? styles.navLinkActive : ''}`}
                style={{ '--link-color': route.color }}
                onClick={() => go(route.path)}
                aria-current={isActive ? 'page' : undefined}
              >
                <span className={styles.navLinkIcon}><Icon /></span>
                <span className={styles.navLinkLabel}>{route.label}</span>
                {isActive && <span className={styles.navLinkDot} />}
              </button>
            );
          })}
        </nav>
      )}
    </header>
  );
}
