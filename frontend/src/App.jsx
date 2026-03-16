import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { NavigationBar } from './components';
import { useTheme } from './hooks';
import Home from './pages/Home/Home';
import BlackjackPage from './pages/Blackjack/BlackjackPage';
import PokerPage from './pages/Poker/PokerPage';
import SnakesAndLaddersPage from './pages/SnakesAndLadders/SnakesAndLaddersPage';
import TicTacToePage from './pages/TicTacToe/TicTacToePage';
import styles from './App.module.css';

function App() {
  const { theme, toggleTheme } = useTheme();

  return (
    <Router>
      <div className={styles.app}>
        <NavigationBar theme={theme} toggleTheme={toggleTheme} />
        <main className={styles.main}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/blackjack" element={<BlackjackPage />} />
            <Route path="/poker" element={<PokerPage />} />
            <Route path="/snakes-and-ladders" element={<SnakesAndLaddersPage />} />
            <Route path="/naughts-and-crosses" element={<TicTacToePage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
