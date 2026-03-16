import { Link, useLocation } from 'react-router-dom';
import { useTheme } from '../../contexts/ThemeContext';
import styles from './Navigation.module.css';

const Navigation = () => {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();

  const navItems = [
    { path: '/', label: 'Home', icon: '🏠' },
    { path: '/blackjack', label: 'Blackjack', icon: '🃏' },
    { path: '/poker', label: 'Poker', icon: '♠️' },
    { path: '/snakes-and-ladders', label: 'Snakes & Ladders', icon: '🎲' },
    { path: '/naughts-and-crosses', label: 'Tic-Tac-Toe', icon: '⭕' },
  ];

  return (
    <nav className={styles.nav}>
      <div className={styles.container}>
        <div className={styles.brand}>
          <span className={styles.logo}>🎰</span>
          <h1 className={styles.title}>Monte Carlo Simulations</h1>
        </div>
        <div className={styles.rightSection}>
          <ul className={styles.navList}>
            {navItems.map((item) => (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`${styles.navLink} ${
                    location.pathname === item.path ? styles.active : ''
                  }`}
                >
                  <span className={styles.icon}>{item.icon}</span>
                  <span className={styles.label}>{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>
          <button
            className={styles.themeToggle}
            onClick={toggleTheme}
            aria-label="Toggle theme"
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
