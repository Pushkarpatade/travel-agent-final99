import React, { useState } from 'react';
import {
  Clock,
  MapPin,
  Navigation,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Landmark,
  Utensils,
  Bus,
  ShieldAlert
} from 'lucide-react';
import { Activity } from '../types';

interface ActivityCardProps {
  activity: Activity;
  currency?: string;
}

export const ActivityCard: React.FC<ActivityCardProps> = ({ activity, currency = '₹' }) => {
  const [showBackup, setShowBackup] = useState(false);

  const getCategoryIcon = (cat: string) => {
    switch (cat.toLowerCase()) {
      case 'restaurant':
        return <Utensils className="w-4 h-4 text-emerald-600" />;
      case 'transport':
        return <Bus className="w-4 h-4 text-amber-600" />;
      default:
        return <Landmark className="w-4 h-4 text-cyan-600" />;
    }
  };

  return (
    <div className={`p-5 rounded-2xl border transition-all ${
      activity.is_cancelled
        ? 'bg-rose-50 border-rose-200 text-slate-700'
        : 'bg-white border-slate-200/80 shadow-sm hover:shadow-md hover:border-slate-300'
    }`}>
      {activity.travel_time_from_prev_mins > 0 && (
        <div className="flex items-center gap-2 mb-3 pb-2.5 border-b border-slate-100 text-xs text-slate-500 font-medium">
          <Navigation className="w-3.5 h-3.5 text-cyan-600" />
          <span>
            {activity.travel_time_from_prev_mins} mins transit ({activity.distance_from_prev_km} km) from previous spot
          </span>
        </div>
      )}

      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-center shrink-0 mt-0.5 shadow-xs">
            {getCategoryIcon(activity.category)}
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className={`font-bold text-base ${activity.is_cancelled ? 'line-through text-rose-600' : 'text-slate-900'}`}>
                {activity.name}
              </h4>
              <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold tracking-wide uppercase bg-slate-100 text-slate-700 border border-slate-200">
                {activity.category}
              </span>
              {activity.is_cancelled && (
                <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-rose-100 text-rose-700 border border-rose-200 flex items-center gap-1">
                  <ShieldAlert className="w-3 h-3" /> Cancelled
                </span>
              )}
            </div>

            {activity.description && (
              <p className="text-sm text-slate-600 mt-1 leading-relaxed">
                {activity.description}
              </p>
            )}
          </div>
        </div>

        {/* Timing & Rupee Cost */}
        <div className="text-right shrink-0">
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-cyan-700 bg-cyan-50 border border-cyan-200 px-3 py-1 rounded-lg shadow-2xs">
            <Clock className="w-3.5 h-3.5" />
            <span>{activity.start_time} - {activity.end_time}</span>
          </div>
          <div className="text-xs font-bold text-slate-900 mt-1">
            {activity.estimated_cost === 0 ? 'Free Entry' : `₹${activity.estimated_cost.toFixed(0)}`}
          </div>
        </div>
      </div>

      {/* Meta details footer */}
      <div className="mt-3.5 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 flex-wrap gap-2">
        <div className="flex items-center gap-4 flex-wrap">
          {activity.location_name && (
            <span className="flex items-center gap-1 font-medium">
              <MapPin className="w-3.5 h-3.5 text-slate-400" />
              {activity.location_name}
            </span>
          )}
          <span className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            Hours: {activity.opening_hours}
          </span>
        </div>

        {activity.backup_option && (
          <button
            onClick={() => setShowBackup(!showBackup)}
            className="flex items-center gap-1 text-xs font-semibold text-cyan-700 hover:text-cyan-800 transition-colors"
          >
            <span>Backup Option</span>
            {showBackup ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        )}
      </div>

      {showBackup && activity.backup_option && (
        <div className="mt-3 p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-cyan-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold text-cyan-700 block mb-0.5">Rain / Contingency Backup:</span>
            <span>{activity.backup_option}</span>
          </div>
        </div>
      )}
    </div>
  );
};
