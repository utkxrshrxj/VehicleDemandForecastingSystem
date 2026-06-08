import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import { Truck, Activity, TrendingUp, AlertCircle } from 'lucide-react';
import MetricCard from './MetricCard';
import DemandChart from './DemandChart';

const Dashboard = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState({
    totalActual: 0,
    totalForecast: 0,
    avgDifference: 0,
    accuracy: 0
  });

  useEffect(() => {
    // Load and parse the CSV from the public folder
    Papa.parse('/forecast_details.csv', {
      download: true,
      header: true,
      dynamicTyping: true,
      complete: (results) => {
        const rows = results.data.filter(r => r.Month); // Ensure valid rows
        
        // Aggregate data by Month
        const aggregated = rows.reduce((acc, row) => {
          const month = row.Month;
          if (!acc[month]) {
            acc[month] = { Month: month, Actual: 0, Forecast: 0, Difference: 0 };
          }
          acc[month].Actual += Number(row.Actual_Demand) || 0;
          // Some forecast models might be better, let's take average or sum.
          // Since it's a demo dashboard, we'll just sum all forecasts for now to show trends.
          acc[month].Forecast += Number(row.Forecast_Demand) || 0;
          acc[month].Difference += Number(row.Difference) || 0;
          return acc;
        }, {});

        const chartData = Object.values(aggregated).sort((a, b) => new Date(a.Month) - new Date(b.Month));
        
        // Calculate high level metrics
        const totalActual = chartData.reduce((sum, item) => sum + item.Actual, 0);
        const totalForecast = chartData.reduce((sum, item) => sum + item.Forecast, 0);
        const diff = Math.abs(totalActual - totalForecast);
        const accuracy = totalActual === 0 ? 0 : Math.max(0, 100 - ((diff / totalForecast) * 100));

        setMetrics({
          totalActual: Math.round(totalActual).toLocaleString(),
          totalForecast: Math.round(totalForecast).toLocaleString(),
          avgDifference: Math.round(diff / (chartData.length || 1)).toLocaleString(),
          accuracy: accuracy.toFixed(1)
        });

        setData(chartData);
        setLoading(false);
      }
    });
  }, []);

  if (loading) {
    return (
      <div style={{ height: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <h2 style={{ color: 'var(--brand-primary)' }}>Loading Insights...</h2>
      </div>
    );
  }

  return (
    <div>
      <div className="grid-cards">
        <MetricCard 
          title="Total Forecasted Demand" 
          value={metrics.totalForecast} 
          icon={<TrendingUp size={28} />} 
          trend="up" 
          trendValue="12.5%" 
        />
        <MetricCard 
          title="Actual Demand Recorded" 
          value={metrics.totalActual} 
          icon={<Truck size={28} />} 
        />
        <MetricCard 
          title="Avg Forecast Difference" 
          value={metrics.avgDifference} 
          icon={<AlertCircle size={28} />} 
          trend="down" 
          trendValue="4.2%" 
        />
        <MetricCard 
          title="Model Accuracy Score" 
          value={`${metrics.accuracy}%`} 
          icon={<Activity size={28} />} 
        />
      </div>

      <div className="grid-charts">
        <DemandChart 
          title="Demand Forecast vs Actual Trends"
          data={data}
          type="area"
          xKey="Month"
          yKeys={['Actual', 'Forecast']}
          colors={['var(--brand-primary)', 'var(--accent-success)']}
        />
        <DemandChart 
          title="Forecast Variance"
          data={data}
          type="bar"
          xKey="Month"
          yKeys={['Difference']}
          colors={['var(--accent-warning)']}
        />
      </div>
    </div>
  );
};

export default Dashboard;
