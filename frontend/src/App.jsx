import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import Navigation from './components/Navigation/Navigation';
import Home from './pages/Home/Home';
import BlackjackPage from './pages/Blackjack/BlackjackPage';
import PokerPage from './pages/Poker/PokerPage';
import SnakesAndLaddersPage from './pages/SnakesAndLadders/SnakesAndLaddersPage';
import NaughtsAndCrossesPage from './pages/NaughtsAndCrosses/NaughtsAndCrossesPage';
import styles from './App.module.css';

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className={styles.app}>
          <Navigation />
          <main className={styles.main}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/blackjack" element={<BlackjackPage />} />
              <Route path="/poker" element={<PokerPage />} />
              <Route path="/snakes-and-ladders" element={<SnakesAndLaddersPage />} />
              <Route path="/naughts-and-crosses" element={<NaughtsAndCrossesPage />} />
            </Routes>
          </main>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
