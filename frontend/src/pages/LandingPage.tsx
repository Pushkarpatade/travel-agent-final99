import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Compass,
  Search,
  ShieldAlert,
  Calendar,
  DollarSign,
  MapPin,
  ArrowRight,
  Zap,
  CheckCircle2,
  Clock,
  Navigation
} from 'lucide-react';
import { Navbar } from '../components/Navbar';

export const LandingPage: React.FC = () => {
  const [destination, setDestination] = useState('');
  const navigate = useNavigate();

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (destination.trim()) {
      navigate('/create-trip', { state: { destination } });
    } else {
      navigate('/create-trip');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col selection:bg-cyan-500 selection:text-white">
      <Navbar />

      {/* Hero Section */}
      <section className="relative pt-16 pb-24 border-b border-slate-200/80 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-50 border border-cyan-200 text-cyan-800 text-xs font-bold uppercase tracking-wider mb-8 shadow-2xs">
            <Sparkles className="w-4 h-4 text-cyan-600" />
            <span>Autonomous Travel Planning & Real-Time Disruption Engine</span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight max-w-4xl mx-auto text-slate-900 leading-tight">
            Plan Smarter.{' '}
            <span className="text-cyan-600">
              Travel Better.
            </span>
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto font-medium leading-relaxed">
            Mindtrip TravelPilot generates personalized day-by-day itineraries using LangGraph agents, live Tavily web search, weather radars, and distance optimization.
          </p>

          {/* Destination Quick Input Form */}
          <form onSubmit={handleSearchSubmit} className="mt-10 max-w-xl mx-auto flex items-center p-2 rounded-2xl bg-white border border-slate-300 shadow-lg">
            <div className="flex items-center gap-3 pl-4 flex-1">
              <MapPin className="w-5 h-5 text-cyan-600 shrink-0" />
              <input
                type="text"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                placeholder="Where do you want to travel? (e.g. Dubai, Mumbai, Pune, Paris)"
                className="w-full bg-transparent border-none text-slate-900 placeholder-slate-400 text-sm focus:outline-none font-medium"
              />
            </div>
            <button
              type="submit"
              className="px-6 py-3 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-sm flex items-center gap-2 transition-all shadow-sm"
            >
              <span>Build Itinerary</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        </div>
      </section>

      {/* Key Features Grid */}
      <section className="py-20 bg-slate-50 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl font-extrabold text-slate-900">Engineered for Modern Travelers</h2>
            <p className="text-slate-600 mt-2 font-medium">
              Beyond simple static text lists—TravelPilot detects schedule conflicts, re-plans rained-out outdoor activities, and calculates precise budget allocations in Rupees (₹).
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-8 rounded-3xl bg-white border border-slate-200 shadow-sm hover:shadow-md transition-all">
              <div className="w-12 h-12 rounded-2xl bg-cyan-50 border border-cyan-200 flex items-center justify-center text-cyan-700 mb-6">
                <Sparkles className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">LangGraph Multi-Agent Workflow</h3>
              <p className="text-sm text-slate-600 leading-relaxed font-medium">
                13-node autonomous graph pipeline checks weather, resolves attraction locations, calculates travel time buffers, and detects timing overlaps.
              </p>
            </div>

            <div className="p-8 rounded-3xl bg-white border border-slate-200 shadow-sm hover:shadow-md transition-all">
              <div className="w-12 h-12 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-700 mb-6">
                <ShieldAlert className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Real-Time Disruption Management</h3>
              <p className="text-sm text-slate-600 leading-relaxed font-medium">
                Rain in the forecast? Cancelled museum pass? Hit "Auto Re-plan" to instantly swap outdoor spots with indoor alternatives.
              </p>
            </div>

            <div className="p-8 rounded-3xl bg-white border border-slate-200 shadow-sm hover:shadow-md transition-all">
              <div className="w-12 h-12 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700 mb-6">
                <DollarSign className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Mindtrip Conversational AI</h3>
              <p className="text-sm text-slate-600 leading-relaxed font-medium">
                Chat directly with your itinerary. Ask "Reduce my budget by 20%", "Flight cost to Dubai", or "PGs in Hadapsar" and get direct booking links!
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Footer */}
      <footer className="py-12 bg-white border-t border-slate-200 text-center text-xs text-slate-500 font-semibold">
        <div className="max-w-7xl mx-auto px-4">
          <p>© 2026 Mindtrip TravelPilot Inc. Intelligent Trip Planning & Disruption Management Agent.</p>
        </div>
      </footer>
    </div>
  );
};
