import React from 'react';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <div className="app-container">
      <header className="header">
        <div>
          <h1 className="header-title">Vehicle Demand Forecasting</h1>
          <p className="header-subtitle">Intelligent insights and predictive analytics for your fleet.</p>
        </div>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'var(--brand-primary)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
            UR
          </div>
        </div>
      </header>
      
      <main>
        <Dashboard />
      </main>
    </div>
  );
}

export default App;
