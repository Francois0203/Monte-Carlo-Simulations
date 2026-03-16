import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FaHome, FaBars, FaTimes } from 'react-icons/fa';
import { GiCardJoker, GiCardRandom, GiSnake, GiTicTacToe } from 'react-icons/gi';
import ThemeSwitch from '../ThemeSwitch';
import styles from './NavigationBar.module.css';

// ============================================
// CONSTANTS
// ============================================

// Icon set for navigation links
const ICONS = [FaHome, GiCardJoker, GiCardRandom, GiSnake, GiTicTacToe];

// ============================================
// NAVIGATION BAR COMPONENT
// ============================================
// Liquid-glass burger menu navigation

const NavigationBar = ({
  theme,
  toggleTheme,
  burgerSize = 50,
  className = ""
}) => {
  // ----------------------------------------
  // State & Refs
  // ----------------------------------------

  const [menuOpen, setMenuOpen] = useState(false);
  const [hoveredLink, setHoveredLink] = useState(null);

  const containerRef = useRef(null);
  const location = useLocation();
  const navigate = useNavigate();

  // ----------------------------------------
  // Navigation Links
  // ----------------------------------------

  const links = [
    { path: '/', label: 'Home' },
    { path: '/blackjack', label: 'Blackjack' },
    { path: '/poker', label: 'Poker' },
    { path: '/snakes-and-ladders', label: 'Snakes & Ladders' },
    { path: '/naughts-and-crosses', label: 'Tic-Tac-Toe' },
  ];

  // ----------------------------------------
  // Derived Helpers
  // ----------------------------------------

  const burgerIconSize = Math.max(18, Math.round(burgerSize * 0.6));

  const isActive = (link) => {
    return location.pathname === link.path;
  };

  // ----------------------------------------
  // Event Handlers
  // ----------------------------------------

  const toggleMenu = () => setMenuOpen((prev) => !prev);

  const closeMenu = () => {
    setMenuOpen(false);
    setHoveredLink(null);
  };

  const handleLinkClick = (link) => {
    navigate(link.path);
    closeMenu();
  };

  // ----------------------------------------
  // Effects
  // ----------------------------------------

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        closeMenu();
      }
    };

    if (menuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [menuOpen]);

  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        closeMenu();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  // ----------------------------------------
  // Render
  // ----------------------------------------

  return (
    <div className={`${styles.navbarContainer} ${className}`} ref={containerRef}>
      <nav className={styles.navbar} aria-label="Main navigation">
        
        {/* Burger Button */}
        <button
          className={`${styles.burger} ${menuOpen ? styles.burgerOpen : ''}`}
          aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
          aria-expanded={menuOpen}
          onClick={toggleMenu}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              toggleMenu();
            }
          }}
          style={{
            width: burgerSize,
            height: burgerSize,
            minWidth: burgerSize,
            minHeight: burgerSize,
          }}
        >
          {menuOpen ? (
            <FaTimes size={burgerIconSize} className={styles.burgerIcon} />
          ) : (
            <FaBars size={burgerIconSize} className={styles.burgerIcon} />
          )}
        </button>

        {/* Dropdown Menu */}
        {menuOpen && (
          <div
            className={`${styles.menuDropdown} ${styles.menuDropdownOpen}`}
            role="menu"
          >
            <ul className={styles.linkList} role="menubar">
              {links.map((link, index) => {
                const Icon = ICONS[index];
                const active = isActive(link);
                const hovered = hoveredLink === index;

                return (
                  <li
                    key={`nav-${index}`}
                    className={styles.linkItem}
                    role="none"
                    onMouseEnter={() => setHoveredLink(index)}
                    onMouseLeave={() => setHoveredLink(null)}
                  >
                    <div
                      className={[
                        styles.link,
                        hovered ? styles.linkHovered : '',
                        active ? styles.linkActive : '',
                      ].join(' ')}
                      onClick={() => handleLinkClick(link)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          handleLinkClick(link);
                        }
                      }}
                      role="menuitem"
                      tabIndex={0}
                      aria-current={active ? 'page' : undefined}
                      data-index={index}
                    >
                      {/* Icon pill */}
                      <div className={styles.linkIcon}>
                        <Icon size={20} />
                      </div>

                      {/* Label */}
                      <span className={styles.linkLabel}>{link.label}</span>
                    </div>
                  </li>
                );
              })}
            </ul>

            {/* Theme Switch in Menu */}
            <div className={styles.themeContainer}>
              <ThemeSwitch theme={theme} toggleTheme={toggleTheme} />
              <span className={styles.themeLabel}>Toggle Theme</span>
            </div>
          </div>
        )}
      </nav>

      {/* Backdrop Overlay - outside nav, below burger */}
      {menuOpen && (
        <div
          className={styles.backdrop}
          onClick={closeMenu}
          aria-hidden="true"
        />
      )}
    </div>
  );
};

// ============================================
// EXPORTS
// ============================================

export default NavigationBar;
