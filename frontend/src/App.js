import React, { useState, useEffect, createContext } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import './App.css';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import Tasks from './pages/Tasks';
import AIInsights from './pages/AIInsights';
import Queries from './pages/Queries';
import Settings from './pages/Settings';
import Login from './pages/Login';
import { supabase } from './api/client';

// Create Date Filter Context
export const DateFilterContext = createContext();

function App() {
  const [activePage, setActivePage] = useState('overview');
  const [dateFilter, setDateFilter] = useState('all'); // 'today', 'week', 'month', 'year', 'all'
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setLoading(false);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  const renderPage = () => {
    switch (activePage) {
      case 'overview':
        return <Overview />;
      case 'tasks':
        return <Tasks />;
      case 'ai-insights':
        return <AIInsights />;
      case 'queries':
        return <Queries />;
      case 'settings':
        return <Settings />;
      default:
        return <Overview />;
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '100vh', 
        background: '#0f172a',
        color: '#fff'
      }}>
        Loading...
      </div>
    );
  }

  if (!session) {
    return <Login />;
  }

  return (
    <Router>
      <DateFilterContext.Provider value={{ dateFilter, setDateFilter, session }}>
        <div className="App">
          <Navbar />
          <div className="app-container">
            <Sidebar activePage={activePage} setActivePage={setActivePage} />
            <main className="main-content">
              {renderPage()}
            </main>
          </div>
        </div>
      </DateFilterContext.Provider>
    </Router>
  );
}

export default App;

