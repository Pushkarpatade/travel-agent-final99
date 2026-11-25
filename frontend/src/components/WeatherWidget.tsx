import React from 'react';
import { Sun, CloudRain, Cloud, Wind, AlertTriangle } from 'lucide-react';
import { WeatherData } from '../types';

interface WeatherWidgetProps {
  weather?: WeatherData;
}

export const WeatherWidget: React.FC<WeatherWidgetProps> = ({ weather }) => {
  if (!weather || !weather.forecast || weather.forecast.length === 0) {
    return (
      <div className="p-4 rounded-2xl bg-white border border-slate-200 text-sm text-slate-500 shadow-xs">
        Weather data loading...
      </div>
    );
  }

  const getWeatherIcon = (iconName: string, rainPct: number) => {
    if (rainPct > 50 || iconName.includes('rain')) {
      return <CloudRain className="w-5 h-5 text-cyan-600" />;
    } else if (rainPct > 20 || iconName.includes('cloud')) {
      return <Cloud className="w-5 h-5 text-slate-400" />;
    }
    return <Sun className="w-5 h-5 text-amber-500" />;
  };

  return (
    <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Weather Forecast</h3>
          <p className="text-xs text-slate-500 font-medium">Live 5-Day Outlook for {weather.destination}</p>
        </div>
        <div className="px-3 py-1 rounded-full bg-cyan-50 border border-cyan-200 text-[11px] font-bold text-cyan-700">
          Smart Radar
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {weather.forecast.slice(0, 5).map((day, idx) => {
          const isHighRain = day.rain_probability_pct >= 50;
          return (
            <div
              key={idx}
              className={`p-3 rounded-xl border text-center transition-all ${
                isHighRain
                  ? 'bg-amber-50 border-amber-200'
                  : 'bg-slate-50 border-slate-200/80'
              }`}
            >
              <div className="text-xs font-bold text-slate-700 mb-2">
                {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short', month: 'numeric', day: 'numeric' })}
              </div>
              
              <div className="flex justify-center mb-2">
                {getWeatherIcon(day.icon, day.rain_probability_pct)}
              </div>

              <div className="text-sm font-bold text-slate-900">
                {Math.round(day.temp_high_c)}°C
                <span className="text-xs font-medium text-slate-500 ml-1">
                  / {Math.round(day.temp_low_c)}°
                </span>
              </div>

              <div className="mt-2.5">
                <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1 font-semibold">
                  <span>Rain</span>
                  <span className={isHighRain ? 'font-bold text-amber-700' : ''}>
                    {day.rain_probability_pct}%
                  </span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${isHighRain ? 'bg-amber-500' : 'bg-cyan-600'}`}
                    style={{ width: `${Math.min(100, day.rain_probability_pct)}%` }}
                  />
                </div>
              </div>

              {isHighRain && (
                <div className="mt-2 flex items-center justify-center gap-1 text-[10px] font-bold text-amber-700">
                  <AlertTriangle className="w-3 h-3" /> Indoor Alert
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
