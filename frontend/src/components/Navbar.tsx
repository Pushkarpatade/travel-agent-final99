import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Compass, User as UserIcon, LogOut, PlusCircle, Sparkles, Radio, Shield } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { LegalModal } from './LegalModal';

export const Navbar: React.FC = () => {
  const { user, logout, token } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [legalModalType, setLegalModalType] = useState<'privacy' | 'terms' | null>(null);

  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';

  return (
    <>
      <header className="border-b border-slate-200 bg-white/95 backdrop-blur-md sticky top-0 z-40 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          
          {/* Brand Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-md group-hover:scale-105 transition-transform">
              <Compass className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-lg sm:text-xl font-bold text-slate-900 tracking-tight">
                TravelPilot <span className="text-cyan-600">AI</span>
              </span>
              <span className="hidden sm:block text-[10px] uppercase tracking-widest text-cyan-600 font-bold">
                Autonomous Multi-Agent Planner
              </span>
            </div>
          </Link>

          {/* Real-Time Live Radar Badge (Visible across all screens) */}
          <div className="hidden md:flex items-center gap-2 py-1 px-3 rounded-full bg-slate-100 border border-slate-200 text-[11px] font-bold text-slate-700">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>LIVE RADAR // REAL-TIME FLIGHT & WEATHER ACTIVE</span>
          </div>

          {/* Navigation Controls */}
          <div className="flex items-center gap-2 sm:gap-4">
            {/* Legal Notice Shortcut */}
            <button
              onClick={() => setLegalModalType('terms')}
              className="text-[11px] font-bold text-slate-500 hover:text-cyan-700 hover:underline px-2 py-1 rounded transition-colors hidden lg:inline-block"
              title="Terms & Real-World Pricing Disclaimers"
            >
              Disclaimers & Terms
            </button>

            {token && user ? (
              <>
                <Link
                  to="/create-trip"
                  className="inline-flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs sm:text-sm shadow-sm transition-all"
                >
                  <PlusCircle className="w-4 h-4" />
                  <span>Plan Trip</span>
                </Link>

                <div className="flex items-center gap-2 sm:gap-3 pl-2 sm:pl-3 border-l border-slate-200">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-cyan-50 border border-cyan-200 flex items-center justify-center text-cyan-700 font-bold text-xs">
                      {user.full_name ? user.full_name[0].toUpperCase() : 'P'}
                    </div>
                    <span className="text-xs sm:text-sm font-bold text-slate-700 hidden sm:inline">
                      {user.full_name?.split(' ')[0]}
                    </span>
                  </div>

                  <button
                    onClick={logout}
                    className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                    title="Sign Out"
                  >
                    <LogOut className="w-4 h-4" />
                  </button>
                </div>
              </>
            ) : !isAuthPage ? (
              <div className="flex items-center gap-2 sm:gap-3">
                <Link
                  to="/login"
                  className="px-3 sm:px-4 py-2 rounded-xl text-slate-700 hover:text-slate-900 font-bold text-xs sm:text-sm transition-colors"
                >
                  Log In
                </Link>
                <Link
                  to="/register"
                  className="px-3 sm:px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs sm:text-sm transition-colors shadow-sm"
                >
                  Get Started
                </Link>
              </div>
            ) : null}
          </div>
        </div>
      </header>

      {/* Legal Modal */}
      {legalModalType && (
        <LegalModal
          isOpen={Boolean(legalModalType)}
          onClose={() => setLegalModalType(null)}
          type={legalModalType}
        />
      )}
    </>
  );
};
