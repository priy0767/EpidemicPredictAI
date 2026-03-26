import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';

const BASE_API_URL = 'https://epidemic-backend.onrender.com/api';

const CovidChoroplethMap = ({ 
  title, 
  subtitle, 
  isPrediction, 
  mapHeight = "400px", 
  onCountryHover, 
  targetDate = "2021-11-05" 
}) => {
  const [geoData, setGeoData] = useState(null);
  const [mapData, setMapData] = useState({});
  const [isLoading, setIsLoading] = useState(true);

  // Theme colors to match the Deep Slate dashboard
  const theme = {
    textMain: '#F3F4F6',
    textMuted: '#9CA3AF',
    cardBg: '#111827',
    border: '1px solid rgba(255, 255, 255, 0.05)',
  };

  // 1. Fetch GeoJSON boundaries
  useEffect(() => {
    axios.get("https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json")
      .then(res => setGeoData(res))
      .catch(err => console.error("Error loading GeoJSON:", err));
  }, []);

  // 2. Fetch Data from Python Backend when Date changes
  useEffect(() => {
    setIsLoading(true);
    const endpoint = isPrediction ? '/global_predictions' : '/map_snapshot';
    
    axios.get(`${BASE_API_URL}${endpoint}?target_date=${targetDate}`)
      .then(res => {
        if (isPrediction) {
          setMapData(res.data.predictions || {});
        } else {
          setMapData(res.data.snapshot || {});
        }
        setIsLoading(false);
      })
      .catch(err => {
        console.error("Error fetching map data:", err);
        setMapData({});
        setIsLoading(false);
      });
  }, [targetDate, isPrediction]);

  // Determine colors based on whether it is Prediction (14-day) or Historical (Total Cases)
  const getColor = (value) => {
    if (value === undefined || value === null) return '#1F2937'; 

    if (isPrediction) {
      return value > 50000 ? '#F87171' : 
             value > 10000 ? '#FBBF24' : 
             value > 0     ? '#34D399' : 
                             '#1F2937';
    } else {
      return value > 10000000 ? '#7F1D1D' : 
             value > 5000000  ? '#B91C1C' : 
             value > 1000000  ? '#EF4444' : 
             value > 500000   ? '#F59E0B' : 
             value > 0        ? '#FBBF24' : 
                                '#1F2937';
    }
  };

  const style = (feature) => {
    const countryName = feature.properties.name;
    const dbName = countryName === "United States of America" ? "USA" : countryName;
    const value = mapData[dbName];

    return {
      fillColor: getColor(value),
      weight: 1,
      opacity: 1,
      color: 'rgba(255, 255, 255, 0.2)', 
      fillOpacity: 0.85
    };
  };

  const onEachFeature = (feature, layer) => {
    const countryName = feature.properties.name;
    const dbName = countryName === "United States of America" ? "USA" : countryName;

    // Hover effect
    layer.on({
      mouseover: (e) => {
        const activeLayer = e.target;
        activeLayer.setStyle({
          weight: 2,
          color: '#00E5FF', 
          fillOpacity: 1
        });
        activeLayer.bringToFront();
        
        if (onCountryHover) {
          onCountryHover(dbName);
        }
      },
      mouseout: (e) => {
        if (geoData) {
          const defaultStyle = style(feature);
          e.target.setStyle(defaultStyle);
        }
      }
    });

    const value = mapData[dbName];
    const displayValue = value ? value.toLocaleString() : "No Data";
    layer.bindTooltip(`<strong>${dbName}</strong><br/>Cases: ${displayValue}`, {
      direction: 'top',
      className: 'custom-map-tooltip'
    });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      
      {/* 👑 Styled Headers */}
      <div style={{ marginBottom: '16px' }}>
        <h2 style={{ margin: '0 0 4px 0', fontSize: '1.25rem', color: theme.textMain, fontWeight: '700' }}>{title}</h2>
        <p style={{ margin: 0, fontSize: '0.9rem', color: theme.textMuted }}>{subtitle}</p>
      </div>

      <div style={{ 
        height: mapHeight, 
        width: '100%', 
        borderRadius: '12px',
        overflow: 'hidden',
        border: theme.border,
        boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.5)',
        position: 'relative',
        backgroundColor: '#0F172A'
      }}>
        
        {isLoading && (
          <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', color: '#00E5FF', zIndex: 1000, fontWeight: '600', letterSpacing: '1px' }}>
            Updating Map...
          </div>
        )}

        <MapContainer 
          style={{ height: '100%', width: '100%', zIndex: 1 }} 
          center={[20, 0]} // Re-centered to [20, 0] to perfectly balance the continents
          
          // 👇 THE FIX: Dropped big map zoom from 2 down to 1.5!
          zoom={isPrediction ? 1.5 : 0.5} 
          minZoom={0.5} 
          zoomSnap={0.5} 
          
          scrollWheelZoom={false} 
          dragging={true} // Click and drag is turned on!
        >
          {/* Dark Mode Basemap */}
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors'
          />
          {geoData && Object.keys(mapData).length > 0 && (
            <GeoJSON 
              key={targetDate + (isPrediction ? 'pred' : 'hist')} 
              data={geoData.data} 
              style={style} 
              onEachFeature={onEachFeature} 
            />
          )}
        </MapContainer>
      </div>

      <style>{`
        .custom-map-tooltip {
          background-color: #111827 !important;
          border: 1px solid rgba(0, 229, 255, 0.3) !important;
          color: #F3F4F6 !important;
          border-radius: 8px !important;
          box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5) !important;
        }
        .leaflet-tooltip-top:before { border-top-color: rgba(0, 229, 255, 0.3) !important; }
      `}</style>
    </div>
  );
};

export default CovidChoroplethMap;