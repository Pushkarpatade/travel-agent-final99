import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  CalendarDays,
  MapPin,
  PieChart,
  AlertTriangle,
  MessageSquare,
  ArrowLeft,
  Compass
} from 'lucide-react';

interface SidebarProps {
  tripId: number;
  destination: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ tripId, destination }) => {
  const navItems = [
    { label: 'Overview', icon: LayoutDashboard, path: `/dashboard/${tripId}` },
    { label: 'Itinerary Plan', icon: CalendarDays, path: `/itinerary/${tripId}` },
    { label: 'Map Explorer', icon: MapPin, path: `/map/${tripId}` },
    { label: 'Budget Breakdown', icon: PieChart, path: `/budget/${tripId}` },
    { label: 'Disruption Center', icon: AlertTriangle, path: `/disruptions/${tripId}` },
    { label: 'AI Travel Assistant', icon: MessageSquare, path: `/chat/${tripId}` },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 min-h-[calc(100vh-4rem)] p-4 flex flex-col justify-between shadow-xs">
      <div>
        <div className="mb-6 px-4 py-3 rounded-2xl bg-slate-50 border border-slate-200">
          <span className="text-[10px] font-bold text-cyan-600 uppercase tracking-wider block mb-0.5">
            Active Trip
          </span>
          <h2 className="text-base font-bold text-slate-900 capitalize truncate">{destination}</h2>
        </div>

        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-semibold text-sm transition-all ${
                    isActive
                      ? 'bg-cyan-50 text-cyan-700 border border-cyan-200 shadow-xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      <div className="pt-4 border-t border-slate-200">
        <NavLink
          to="/dashboard"
          className="flex items-center gap-2 px-3 py-2 text-xs font-semibold text-slate-500 hover:text-slate-800 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>All Trips</span>
        </NavLink>
      </div>
    </aside>
  );
};
