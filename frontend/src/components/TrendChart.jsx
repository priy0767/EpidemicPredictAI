import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const BASE_API_URL = 'https://epidemic-backend.onrender.com/api';

const TrendChart = ({ country = "India", targetDate = "2021-11-05", mobility }) => {
  const [trendData, setTrendData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Theme variables to match App.jsx
  const theme = {
    cardBg: '#111827',
    border: '1px solid rgba(99, 102, 241, 0.15)',
    textMuted: '#9CA3AF',
    accent: '#00E5FF',  // Neon Cyan for actuals
    danger: '#F87171',  // Soft Coral for predictions
    gridLine: 'rgba(255,255,255,0.05)'
  };

  useEffect(() => {
    setIsLoading(true);
    axios.post(`${BASE_API_URL}/predict`, {
      country: country,
      region: "All",
      target_date: targetDate,
      daily_cases_7d_avg: 5000, 
      retail_recreation_lag14: mobility?.retail || 0,
      transit_stations_lag14: mobility?.transit || 0,
      workplaces_lag14: mobility?.work || 0,
      residential_lag14: mobility?.residential || 0
    })
    .then(res => {
      let rawData = res.data.trend_data;
      if (!Array.isArray(rawData)) rawData = [];
      setTrendData(rawData);
      setIsLoading(false);
    })
    .catch(err => {
      console.error("Error fetching trend data", err);
      setTrendData([]);
      setIsLoading(false);
    });
  }, [country, targetDate, mobility]);

  if (isLoading) {
    return <div style={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center', color: theme.textMuted, fontStyle: 'italic' }}>Simulating timeline...</div>;
  }

  if (!trendData || trendData.length === 0) {
    return (
      <div style={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', color: theme.danger }}>
        <p style={{ margin: 0, fontSize: '0.95rem' }}>No temporal data available for {country}.</p>
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: 250 }}>
      <ResponsiveContainer width="99%" height={250}>
        <AreaChart data={trendData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={theme.accent} stopOpacity={0.6}/>
              <stop offset="95%" stopColor={theme.accent} stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={theme.danger} stopOpacity={0.6}/>
              <stop offset="95%" stopColor={theme.danger} stopOpacity={0}/>
            </linearGradient>
          </defs>
          
          {/* Softer grid lines */}
          <CartesianGrid strokeDasharray="3 3" stroke={theme.gridLine} vertical={false} />
          
          <XAxis dataKey="date" stroke={theme.textMuted} fontSize={12} tickLine={false} axisLine={false} />
          <YAxis stroke={theme.textMuted} fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`} />
          
          <Tooltip 
            contentStyle={{ backgroundColor: theme.cardBg, border: theme.border, color: '#F3F4F6', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.5)' }}
            itemStyle={{ color: '#F3F4F6' }}
          />
          
          {/* Cyan area for actual historical cases */}
          <Area type="monotone" dataKey="actual" name="Actual Cases" stroke={theme.accent} strokeWidth={3} fillOpacity={1} fill="url(#colorActual)" />
          
          {/* Coral Red area for the AI prediction */}
          <Area type="monotone" dataKey="predicted" name="Predicted Next Week" stroke={theme.danger} strokeWidth={3} strokeDasharray="6 6" fillOpacity={1} fill="url(#colorPredicted)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TrendChart;