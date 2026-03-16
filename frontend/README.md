# Monte Carlo Simulations - Frontend

React + Vite frontend for the Monte Carlo Simulations application.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file (already created):
```env
VITE_API_URL=http://localhost:8000
```

3. Start the development server:
```bash
npm run dev
```

4. Access the application:
- Frontend: http://localhost:5173
- API Documentation: http://localhost:8000/docs

## Features

- **Blackjack Simulation**: Test 8 different strategies with configurable rules
- **Poker Simulation**: Analyze Texas Hold'em strategies with customizable blinds and stacks
- **Snakes & Ladders**: Explore probability distributions with configurable board parameters
- **Tic-Tac-Toe**: Statistical analysis of random play on various board sizes

## Tech Stack

- **React 19**: UI framework
- **Vite**: Build tool and dev server
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **CSS Modules**: Component-scoped styling

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable components
│   │   ├── Navigation/     # Main navigation bar
│   │   ├── LoadingSpinner/ # Loading indicator
│   │   └── ErrorMessage/   # Error display component
│   ├── pages/              # Page components
│   │   ├── Home/           # Landing page
│   │   ├── Blackjack/      # Blackjack simulation page
│   │   ├── Poker/          # Poker simulation page
│   │   ├── SnakesAndLadders/ # Snakes & Ladders page
│   │   └── NaughtsAndCrosses/ # Tic-Tac-Toe page
│   ├── utils/              # Utility functions
│   │   └── api.js          # API client configuration
│   ├── App.jsx             # Main app component with routing
│   ├── main.jsx            # Application entry point
│   └── index.css           # Global styles
├── package.json
├── vite.config.js
└── .env                    # Environment variables
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Component Structure

Each page follows a consistent pattern:
1. Configuration form in a sticky sidebar
2. Results display in the main content area
3. Loading and error states
4. Responsive design with CSS modules

## Styling

- CSS Modules for component-scoped styles
- CSS custom properties (variables) for theming
- Responsive design for mobile, tablet, and desktop
- Consistent design system with colors, spacing, and typography

## API Integration

The app communicates with the FastAPI backend through Axios:
- Base URL: `http://localhost:8000`
- Endpoints: `/api/{simulation}/simulate`
- Request/Response validation via Pydantic schemas

## Development

To add a new simulation:
1. Create a new page component in `src/pages/`
2. Create corresponding CSS module
3. Add API methods in `src/utils/api.js`
4. Add route in `src/App.jsx`
5. Add navigation link in `src/components/Navigation/Navigation.jsx`
