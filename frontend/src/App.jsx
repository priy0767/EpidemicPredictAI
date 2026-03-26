import React, { useState, useEffect } from 'react';
import CovidChoroplethMap from './components/CovidChoroplethMap';
import FeatureChart from './components/FeatureChart';
import TrendChart from './components/TrendChart';

function App() {
  // 🚀 Global Boot-up State
  const [isBooting, setIsBooting] = useState(true);
  
  const [hoveredCountry, setHoveredCountry] = useState("India");
  const [targetDate, setTargetDate] = useState("2021-11-05");
  
  const [mobility, setMobility] = useState({
    retail: 0,
    transit: 0,
    work: 0,
    residential: 0
  });

  // Theme configuration
  const theme = {
    bg: '#0B1120',          
    cardBg: '#111827',      
    border: '1px solid rgba(99, 102, 241, 0.15)', 
    textMain: '#F3F4F6',    
    textMuted: '#9CA3AF',   
    accent: '#00E5FF',      
    shadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
  };

  // ⏳ THE TIMER: Hold the loading screen for 2.5 seconds
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsBooting(false);
    }, 2500); 
    return () => clearTimeout(timer);
  }, []);

  const handleSliderChange = (e, type) => {
    setMobility({ ...mobility, [type]: parseInt(e.target.value) });
  };

  // 🎬 THE LOADING SCREEN UI
  if (isBooting) {
    return (
      <div style={{ backgroundColor: theme.bg, height: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: theme.accent, fontFamily: "'Inter', 'Segoe UI', sans-serif" }}>
        
        <style>
          {`
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
          `}
        </style>
        
        <div style={{
          width: '60px', height: '60px', 
          border: '4px solid rgba(0, 229, 255, 0.1)', 
          borderTop: `4px solid ${theme.accent}`, 
          borderRadius: '50%', 
          animation: 'spin 1s linear infinite',
          boxShadow: `0 0 15px ${theme.accent}`,
          marginBottom: '30px'
        }}></div>
        
        <h2 style={{ margin: 0, letterSpacing: '3px', fontSize: '1.5rem', animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite', fontWeight: '700' }}>
          INITIALIZING AI ENGINE
        </h2>
        <p style={{ color: theme.textMuted, marginTop: '10px', fontSize: '0.95rem' }}>
          Loading XGBoost Global Predictive Models...
        </p>
      </div>
    );
  }

  // 🌍 THE MAIN DASHBOARD UI
  return (
    <div style={{ backgroundColor: theme.bg, minHeight: '100vh', padding: '32px', color: theme.textMain, fontFamily: "'Inter', 'Segoe UI', sans-serif" }}>
      
      {/* 👑 NEW BRAND LOGO & HEADER */}
      <header style={{ borderBottom: theme.border, paddingBottom: '24px', marginBottom: '32px', display: 'flex', justifyContent: 'flex-start', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          
          {/* 🌟 The Glowing Logo Box */}
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            width: '48px', height: '48px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(0, 229, 255, 0.15))',
            border: '1px solid rgba(0, 229, 255, 0.3)',
            boxShadow: '0 0 20px rgba(0, 229, 255, 0.15)',
            fontSize: '1.8rem'
          }}>
            🦠
          </div>

          {/* 📝 The Title and Badge */}
          <h1 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span style={{ 
              fontSize: '2.2rem', 
              fontWeight: '800', 
              letterSpacing: '-0.5px',
              background: 'linear-gradient(90deg, #6366f1, #00E5FF)', 
              WebkitBackgroundClip: 'text', 
              WebkitTextFillColor: 'transparent',
              lineHeight: '1.2',           // 👈 THE FIX for chopped text
              paddingBottom: '4px'         // 👈 THE FIX for chopped text
            }}>
              EPIDEMIC PREDICT PRO
            </span>
            
            {/* 💊 The "Global Dashboard" Pill Badge */}
            <span style={{ 
              backgroundColor: 'rgba(0, 229, 255, 0.1)', 
              color: theme.accent, 
              fontSize: '0.85rem', 
              fontWeight: '600', 
              padding: '6px 14px', 
              borderRadius: '20px', 
              border: '1px solid rgba(0, 229, 255, 0.25)',
              letterSpacing: '0.5px',
              textTransform: 'uppercase',
              boxShadow: '0 0 10px rgba(0, 229, 255, 0.1)'
            }}>
              Global Dashboard
            </span>
          </h1>

        </div>
      </header>

      {/* 📅 GLOBAL TIME MACHINE */}
      <div style={{ backgroundColor: theme.cardBg, borderRadius: '16px', padding: '20px 32px', border: theme.border, boxShadow: theme.shadow, marginBottom: '32px', display: 'flex', alignItems: 'center', gap: '24px' }}>
        <h3 style={{ margin: 0, color: theme.textMain, fontSize: '1.05rem', fontWeight: '600', letterSpacing: '0.5px' }}>Global Time Machine</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <label style={{ color: theme.textMuted, fontSize: '0.95rem' }}>Target Date:</label>
          <input 
            type="date" 
            value={targetDate} 
            min="2020-03-01" 
            max="2023-03-09" 
            onChange={(e) => setTargetDate(e.target.value)}
            style={{ 
              padding: '10px 16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', 
              backgroundColor: '#1F2937', color: 'white', outline: 'none', cursor: 'pointer', fontFamily: 'inherit',
              boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.2)'
            }} 
          />
        </div>
        <span style={{ color: theme.textMuted, fontSize: '0.9rem', fontStyle: 'italic', marginLeft: 'auto' }}>
          *Rewinding AI predictions based on historical states.
        </span>
      </div>

      <div style={{ display: 'flex', gap: '32px', maxWidth: '1800px', margin: '0 auto' }}>
        
        {/* ================= LEFT COLUMN ================= */}
        <div style={{ flex: '2.3', display: 'flex', flexDirection: 'column', gap: '32px' }}>
          
          <div style={{ backgroundColor: theme.cardBg, borderRadius: '16px', padding: '24px', border: theme.border, boxShadow: theme.shadow }}>
            <CovidChoroplethMap 
              title="Predicted Outbreak Risk (Next 14 Days)" 
              subtitle="Simulated risk levels based on mobility and historical momentum."
              isPrediction={true} 
              mapHeight="540px" 
              onCountryHover={setHoveredCountry} 
              targetDate={targetDate} 
            />
          </div>

          <div style={{ backgroundColor: theme.cardBg, borderRadius: '16px', padding: '24px', border: theme.border, boxShadow: theme.shadow }}>
             <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h3 style={{ margin: 0, color: theme.textMain, fontSize: '1.1rem', fontWeight: '600' }}>Temporal Trendlines & Prediction</h3>
                <span style={{ color: theme.textMuted, fontSize: '0.95rem', backgroundColor: '#1F2937', padding: '6px 12px', borderRadius: '20px' }}>
                  Region: <strong style={{color: theme.accent}}>{hoveredCountry}</strong>
                </span>
             </div>
             <TrendChart country={hoveredCountry} mobility={mobility} targetDate={targetDate} />
          </div>

        </div>

        {/* ================= RIGHT COLUMN ================= */}
        <div style={{ flex: '1.2', display: 'flex', flexDirection: 'column', gap: '32px' }}>
          
          <div style={{ backgroundColor: theme.cardBg, borderRadius: '16px', padding: '24px', border: theme.border, boxShadow: theme.shadow }}>
            <CovidChoroplethMap 
              title="World Choropleth Map" 
              subtitle="Actual Recorded Total Cases"
              isPrediction={false} 
              mapHeight="240px" 
              targetDate={targetDate} 
            />
          </div>

          <div style={{ backgroundColor: theme.cardBg, borderRadius: '16px', padding: '24px', border: theme.border, boxShadow: theme.shadow }}>
            <h3 style={{ margin: '0 0 8px 0', color: theme.textMain, fontSize: '1.1rem', fontWeight: '600' }}>What-If Scenario Simulator</h3>
            <p style={{ color: theme.textMuted, fontSize: '0.9rem', marginBottom: '24px', lineHeight: '1.5' }}>Adjust mobility factors to simulate lockdown effects on the timeline.</p>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', marginBottom: '8px', fontWeight: '500' }}>
                  <span>Shopping & Leisure</span>
                  <span style={{ color: mobility.retail > 0 ? '#F87171' : theme.accent }}>{mobility.retail > 0 ? '+' : ''}{mobility.retail}%</span>
                </div>
                <input type="range" min="-100" max="100" value={mobility.retail} onChange={(e) => handleSliderChange(e, 'retail')} style={{ width: '100%', cursor: 'pointer', accentColor: theme.accent }} />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', marginBottom: '8px', fontWeight: '500' }}>
                  <span>Public Transit</span>
                  <span style={{ color: mobility.transit > 0 ? '#F87171' : theme.accent }}>{mobility.transit > 0 ? '+' : ''}{mobility.transit}%</span>
                </div>
                <input type="range" min="-100" max="100" value={mobility.transit} onChange={(e) => handleSliderChange(e, 'transit')} style={{ width: '100%', cursor: 'pointer', accentColor: theme.accent }} />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', marginBottom: '8px', fontWeight: '500' }}>
                  <span>Commuting to Work</span>
                  <span style={{ color: mobility.work > 0 ? '#F87171' : theme.accent }}>{mobility.work > 0 ? '+' : ''}{mobility.work}%</span>
                </div>
                <input type="range" min="-100" max="100" value={mobility.work} onChange={(e) => handleSliderChange(e, 'work')} style={{ width: '100%', cursor: 'pointer', accentColor: theme.accent }} />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', marginBottom: '8px', fontWeight: '500' }}>
                  <span>Time at Home</span>
                  <span style={{ color: mobility.residential < 0 ? '#F87171' : theme.accent }}>{mobility.residential > 0 ? '+' : ''}{mobility.residential}%</span>
                </div>
                <input type="range" min="-100" max="100" value={mobility.residential} onChange={(e) => handleSliderChange(e, 'residential')} style={{ width: '100%', cursor: 'pointer', accentColor: theme.accent }} />
              </div>
            </div>
          </div>

          <div style={{ backgroundColor: theme.cardBg, borderRadius: '16px', padding: '24px', border: theme.border, boxShadow: theme.shadow, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
            <h3 style={{ margin: '0 0 8px 0', color: theme.textMain, fontSize: '1.1rem', fontWeight: '600' }}>XGBoost Feature Importance</h3>
            <p style={{ color: theme.textMuted, fontSize: '0.9rem', marginBottom: '20px' }}>
              Primary drivers of spread (Regional Focus: <strong style={{color: theme.accent}}>{hoveredCountry}</strong>)
            </p>
            <div style={{ flexGrow: 1, minHeight: '220px' }}>
              <FeatureChart country={hoveredCountry} targetDate={targetDate} /> 
            </div>
          </div>
          
        </div>

      </div>
    </div>
  );
}

export default App;