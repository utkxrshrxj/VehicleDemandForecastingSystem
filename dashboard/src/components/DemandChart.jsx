import React from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart
} from 'recharts';

const DemandChart = ({ data, type = 'line', xKey, yKeys, colors, title }) => {
  return (
    <div className="chart-container">
      <div className="chart-header">
        <h3 className="chart-title">{title}</h3>
      </div>
      <div style={{ width: '100%', height: 350 }}>
        <ResponsiveContainer>
          {type === 'line' ? (
            <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-color)" />
              <XAxis dataKey={xKey} axisLine={false} tickLine={false} tick={{fill: 'var(--text-secondary)'}} dy={10} />
              <YAxis axisLine={false} tickLine={false} tick={{fill: 'var(--text-secondary)'}} dx={-10} />
              <Tooltip 
                contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: 'var(--shadow-md)' }}
                cursor={{ stroke: 'var(--border-color)', strokeWidth: 2 }}
              />
              <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px' }} />
              {yKeys.map((key, index) => (
                <Line 
                  key={key} 
                  type="monotone" 
                  dataKey={key} 
                  stroke={colors[index] || 'var(--brand-primary)'} 
                  strokeWidth={3}
                  dot={{ r: 4, strokeWidth: 2 }}
                  activeDot={{ r: 6 }}
                />
              ))}
            </LineChart>
          ) : type === 'bar' ? (
            <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-color)" />
              <XAxis dataKey={xKey} axisLine={false} tickLine={false} tick={{fill: 'var(--text-secondary)'}} dy={10} />
              <YAxis axisLine={false} tickLine={false} tick={{fill: 'var(--text-secondary)'}} dx={-10} />
              <Tooltip 
                contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: 'var(--shadow-md)' }}
                cursor={{ fill: 'var(--bg-primary)' }}
              />
              <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px' }} />
              {yKeys.map((key, index) => (
                <Bar 
                  key={key} 
                  dataKey={key} 
                  fill={colors[index] || 'var(--brand-primary)'} 
                  radius={[4, 4, 0, 0]}
                />
              ))}
            </BarChart>
          ) : (
            <AreaChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <defs>
                <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={colors[0] || 'var(--brand-primary)'} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={colors[0] || 'var(--brand-primary)'} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-color)" />
              <XAxis dataKey={xKey} axisLine={false} tickLine={false} tick={{fill: 'var(--text-secondary)'}} dy={10} />
              <YAxis axisLine={false} tickLine={false} tick={{fill: 'var(--text-secondary)'}} dx={-10} />
              <Tooltip 
                contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: 'var(--shadow-md)' }}
              />
              <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px' }} />
              {yKeys.map((key, index) => (
                <Area 
                  key={key} 
                  type="monotone" 
                  dataKey={key} 
                  stroke={colors[index] || 'var(--brand-primary)'} 
                  fillOpacity={1} 
                  fill={`url(#colorActual)`} 
                  strokeWidth={3}
                />
              ))}
            </AreaChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default DemandChart;
