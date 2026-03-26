import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const BASE_API_URL = 'https://epidemic-backend.onrender.com/api';

// 🎨 BRAND NEW: A Custom, Hacker-Style Tooltip!
const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{ 
        backgroundColor: '#111827', 
        border: '1px solid rgba(0, 229, 255, 0.3)', 
        padding: '12px 16px', 
        borderRadius: '8px', 
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)' 
      }}>
        <p style={{ margin: 0, color: '#F3F4F6', fontSize: '0.9rem', fontWeight: '600' }}>
          {payload[0].payload.name}
        </p>
        <p style={{ margin: '6px 0 0 0', color: '#00E5FF', fontSize: '0.85rem', fontWeight: '500' }}>
          Impact Weight: <span style={{ color: '#F3F4F6', fontSize: '1rem', marginLeft: '4px' }}>{payload[0].value}%</span>
        </p>
      </div>
    );
  }
  return null;
};

const FeatureChart = ({ country = "India", targetDate = "2021-11-05" }) => {
  const [featureData, setFeatureData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const theme = {
    cardBg: '#111827',
    border: '1px solid rgba(99, 102, 241, 0.15)',
    textMuted: '#9CA3AF',
    accent: '#00E5FF',
  };

  useEffect(() => {
    setIsLoading(true);
    axios.post(`${BASE_API_URL}/predict`, {
      country: country,
      region: "All",
      target_date: targetDate,
      daily_cases_7d_avg: 5000, 
      retail_recreation_lag14: 0,
      transit_stations_lag14: 0,
      workplaces_lag14: 0,
      residential_lag14: 0
    })
    .then(res => {
      let rawData = res.data.feature_importance;
      if (!Array.isArray(rawData)) rawData = [];
      
      const nameTranslator = {
        "Retail And Recreation": "Shopping & Leisure",
        "Retail & Recreation": "Shopping & Leisure",
        "Transit Stations": "Public Transit",
        "Workplaces": "Commuting to Work",
        "Residential": "Time at Home",
        "Current Cases": "Previous Case Momentum"
      };

      const friendlyData = rawData.map(item => {
        if (!item || typeof item !== 'object') return { name: "Unknown", impact: 0 };
        return {
          ...item,
          name: nameTranslator[item.name] || item.name || "Unknown"
        };
      });

      setFeatureData(friendlyData);
      setIsLoading(false);
    })
    .catch(err => {
      console.error("Error fetching feature importance", err);
      setFeatureData([]);
      setIsLoading(false);
    });
  }, [country, targetDate]);

  if (isLoading) {
    return <div style={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center', color: theme.textMuted, fontStyle: 'italic' }}>Analyzing model drivers...</div>;
  }

  if (!featureData || featureData.length === 0) {
    return (
      <div style={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', color: '#F87171', backgroundColor: 'rgba(248, 113, 113, 0.05)', borderRadius: '12px', padding: '20px', border: '1px dashed rgba(248, 113, 113, 0.2)' }}>
        <p style={{ margin: 0, fontSize: '0.95rem' }}>
          <strong>Insufficient Training Data</strong><br/>
          <span style={{ color: theme.textMuted, fontSize: '0.85rem' }}>AI model drivers unavailable for this region.</span>
        </p>
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: 250 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart layout="vertical" data={featureData} margin={{ top: 10, right: 30, left: 40, bottom: 0 }}>
          <XAxis type="number" hide />
          <YAxis 
            dataKey="name" 
            type="category" 
            stroke={theme.textMuted} 
            fontSize={12} 
            width={130} 
            tickLine={false} 
            axisLine={false} 
          />
          {/* 👇 We tell Recharts to use our custom tooltip here! */}
          <Tooltip 
            cursor={{ fill: 'rgba(255,255,255,0.04)' }} 
            content={<CustomTooltip />} 
          />
          <Bar dataKey="impact" radius={[0, 6, 6, 0]} barSize={20}>
            {featureData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={theme.accent} fillOpacity={0.85} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default FeatureChart;