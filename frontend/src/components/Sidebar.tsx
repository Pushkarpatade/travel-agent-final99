import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  CalendarDays,
  MapPin,
  PieChart,
  AlertTriangle,
  MessageSquare,
  ArrowLeft
} from 'lucide-react';

interface SidebarProps {
  tripId: number;
  destination: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ tripId, destination }) => {
  const navItems = [
    { label: 'Overview', icon: LayoutDashboard, path: `/dashboard/${tripId}` },
    { label: 'Itinerary', icon: CalendarDays, path: `/itinerary/${tripId}` },
    { label: 'Map', icon: MapPin, path: `/map/${tripId}` },
    { label: 'Budget', icon: PieChart, path: `/budget/${tripId}` },
    { label: 'Disruptions', icon: AlertTriangle, path: `/disruptions/${tripId}` },
    { label: 'AI Chat', icon: MessageSquare, path: `/chat/${tripId}` },
  ];

  return (
    <>
      {/* Mobile Top Navigation Bar (Horizontal Swipeable Tabs) */}
      <div className="md:hidden w-full bg-white border-b border-slate-200 sticky top-16 z-30 shadow-xs">
        <div className="px-4 py-2 flex items-center justify-between border-b border-slate-100 bg-slate-50/80">
          <div className="flex items-center gap-2 truncate">
            <span className="text-[10px] font-bold text-cyan-700 bg-cyan-100 px-2 py-0.5 rounded-full uppercase">
              Trip
            </span>
            <span className="text-xs font-bold text-slate-800 capitalize truncate">{destination}</span>
          </div>
          <NavLink
            to="/dashboard"
            className="text-[11px] font-semibold text-slate-500 hover:text-slate-800 flex items-center gap-1 shrink-0 ml-2"
          >
            <ArrowLeft className="w-3 h-3" />
            <span>All Trips</span>
          </NavLink>
        </div>

        <nav className="flex items-center gap-1.5 px-3 py-2 overflow-x-auto no-scrollbar scroll-smooth">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap shrink-0 transition-all ${
                    isActive
                      ? 'bg-cyan-600 text-white shadow-xs'
                      : 'text-slate-600 bg-slate-100 hover:bg-slate-200 hover:text-slate-900'
                  }`
                }
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Desktop Left Sidebar */}
      <aside className="hidden md:flex w-64 bg-white border-r border-slate-200 min-h-[calc(100vh-4rem)] p-4 flex-col justify-between shadow-xs shrink-0">
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
                  <span>{item.label === 'Itinerary' ? 'Itinerary Plan' : item.label === 'Budget' ? 'Budget Breakdown' : item.label === 'Disruptions' ? 'Disruption Center' : item.label === 'AI Chat' ? 'AI Travel Assistant' : item.label}</span>
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
    </>
  );
};
