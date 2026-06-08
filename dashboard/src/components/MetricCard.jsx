import React from 'react';

const MetricCard = ({ title, value, icon, trend, trendValue }) => {
  return (
    <div className="metric-card">
      <div className="metric-icon-box">
        {icon}
      </div>
      <div className="metric-content">
        <span className="metric-label">{title}</span>
        <span className="metric-value">{value}</span>
        {trend && (
          <div style={{ marginTop: '8px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ 
              color: trend === 'up' ? 'var(--accent-success)' : 'var(--accent-error)',
              fontWeight: 600 
            }}>
              {trend === 'up' ? '▲' : '▼'} {trendValue}
            </span>
            <span style={{ color: 'var(--text-secondary)' }}>vs last month</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default MetricCard;
