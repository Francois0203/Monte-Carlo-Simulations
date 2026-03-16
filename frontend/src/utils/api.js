/**
 * API utility for communicating with the backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Blackjack API
export const blackjackApi = {
  simulate: (config) => api.post('/api/blackjack/simulate', config),
  getStrategies: () => api.get('/api/blackjack/strategies'),
};

// Poker API
export const pokerApi = {
  simulate: (config) => api.post('/api/poker/simulate', config),
  getStrategies: () => api.get('/api/poker/strategies'),
};

// Snakes and Ladders API
export const snakesAndLaddersApi = {
  simulate: (config) => api.post('/api/snakes-and-ladders/simulate', config),
};

// Naughts and Crosses API
export const naughtsAndCrossesApi = {
  simulate: (config) => api.post('/api/naughts-and-crosses/simulate', config),
};

// Health check
export const healthCheck = () => api.get('/health');

export default api;
