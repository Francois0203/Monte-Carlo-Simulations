import { useState, useEffect } from 'react';

export const getInitialTheme = () => {
  const sessionInfo = localStorage.getItem('userSessionInfo');
  if (sessionInfo) {
    try {
      const parsed = JSON.parse(sessionInfo);
      if (parsed.prefersColorScheme) return parsed.prefersColorScheme;
    } catch {
      // fallback to browser default
    }
  }

  // Use browser default if no stored preference
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  return prefersDark ? 'dark' : 'light';
};

export const useTheme = () => {
  const [theme, setTheme] = useState(getInitialTheme());

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);

    const sessionInfo = localStorage.getItem('userSessionInfo');
    let updatedInfo = {};

    if (sessionInfo) {
      try {
        updatedInfo = JSON.parse(sessionInfo);
      } catch {
        updatedInfo = {};
      }
    }

    updatedInfo.prefersColorScheme = theme;
    localStorage.setItem('userSessionInfo', JSON.stringify(updatedInfo));
  }, [theme]);

  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  return { theme, toggleTheme, setTheme };
};
