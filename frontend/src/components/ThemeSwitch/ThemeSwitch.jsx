import React, { useState } from 'react';
import { FaSun, FaMoon } from 'react-icons/fa';
import styles from './ThemeSwitch.module.css';

const ThemeSwitch = ({ theme, toggleTheme }) => {
  const [isPressed, setIsPressed] = useState(false);

  const handlePointerDown = () => setIsPressed(true);
  const handlePointerUp = () => setIsPressed(false);

  return (
    <button
      className={`${styles.themeSwitch} ${isPressed ? styles.pressed : ''}`}
      onClick={toggleTheme}
      onPointerDown={handlePointerDown}
      onPointerUp={handlePointerUp}
      onPointerLeave={handlePointerUp}
      aria-label="Toggle theme"
      type="button"
    >
      <span className={styles.icon} aria-hidden="true">
        {theme === 'dark' ? <FaSun /> : <FaMoon />}
      </span>
    </button>
  );
};

export default ThemeSwitch;
