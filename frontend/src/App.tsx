import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { SessionProvider } from './state/SessionContext';
import { Layout } from './Layout';
import { Home } from './pages/Home';
import { Session } from './pages/Session';
import { LangGraphVisualizer } from './pages/LangGraphVisualizer';

function App() {
  return (
    <Router>
      <SessionProvider>
        <Routes>
          {/* Home page uses the full Nyaya-Setu Layout (navbar, footer, sidebar) */}
          <Route element={<Layout />}>
            <Route path="/" element={<Home />} />
          </Route>

          {/* Session and Pipeline are standalone full-screen pages (no layout shell) */}
          <Route path="/session" element={<Session />} />
          <Route path="/pipeline" element={<LangGraphVisualizer />} />
        </Routes>
      </SessionProvider>
    </Router>
  );
}

export default App;
