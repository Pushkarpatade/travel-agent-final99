import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  CalendarDays,
  RefreshCw,
  Sparkles,
  Clock,
  MapPin,
  Utensils,
  Bus,
  Hotel,
  Lightbulb,
  Bookmark,
  MessageSquare,
  Image as ImageIcon,
  ExternalLink
} from 'lucide-react';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { ActivityCard } from '../components/ActivityCard';
import { tripService } from '../services/api';
import { Trip, Itinerary, ItineraryDay } from '../types';

export const ItineraryPage: React.FC = () => {
  const { tripId } = useParams<{ tripId: string }>();

  const [trip, setTrip] = useState<Trip | null>(null);
  const [itinerary, setItinerary] = useState<Itinerary | null>(null);
  const [activeDayIdx, setActiveDayIdx] = useState<number>(0);
  const [activeTab, setActiveTab] = useState<string>('Itinerary');
  const [loading, setLoading] = useState<boolean>(true);
  const [replanning, setReplanning] = useState<boolean>(false);

  useEffect(() => {
    if (tripId) {
      const id = parseInt(tripId);
      Promise.all([tripService.getTrip(id), tripService.getItinerary(id)])
        .then(([t, itin]) => {
          setTrip(t);
          setItinerary(itin);
        })
        .finally(() => setLoading(false));
    }
  }, [tripId]);

  const handleReplan = async () => {
    if (!tripId) return;
    setReplanning(true);
    try {
      const itin = await tripService.replanTrip(parseInt(tripId));
      setItinerary(itin);
    } finally {
      setReplanning(false);
    }
  };

  const currentDay: ItineraryDay | undefined = itinerary?.days && itinerary.days.length > activeDayIdx
    ? itinerary.days[activeDayIdx]
    : undefined;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <Navbar />

      <div className="flex-1 flex flex-col md:flex-row">
        {trip && <Sidebar tripId={trip.id} destination={trip.destination} />}

        <main className="flex-1 p-4 sm:p-6 md:p-8 space-y-6 max-w-5xl">
          
          {/* Header Title */}
          <div className="flex items-center justify-between flex-wrap gap-4 pb-4 border-b border-slate-200">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-100 border border-cyan-200 text-cyan-800 text-xs font-bold uppercase tracking-wider mb-2">
                <Sparkles className="w-3.5 h-3.5 text-cyan-600" />
                LangGraph AI Itinerary
              </div>
              <h1 className="text-3xl font-bold text-slate-900 capitalize">
                Trip to {trip?.destination}
              </h1>
              <p className="text-xs font-semibold text-slate-500 mt-1">
                Estimated Total Cost: <strong className="text-emerald-700">₹{itinerary?.total_estimated_cost.toFixed(0)}</strong>
              </p>
            </div>

            <button
              onClick={handleReplan}
              disabled={replanning}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs shadow-sm transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${replanning ? 'animate-spin' : ''}`} />
              <span>{replanning ? 'Re-planning Itinerary...' : 'Re-plan Itinerary'}</span>
            </button>
          </div>

          {/* Mindtrip Sub-Header Tabs */}
          <div className="flex items-center gap-6 border-b border-slate-200 text-sm font-semibold text-slate-600 overflow-x-auto no-scrollbar">
            {['Itinerary', 'Ideas', 'Bookings', 'Transportation', 'Cuisine'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`pb-3 border-b-2 transition-colors whitespace-nowrap ${
                  activeTab === tab
                    ? 'border-cyan-600 text-cyan-700 font-bold'
                    : 'border-transparent hover:text-slate-900'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Main Tab Views */}
          {activeTab === 'Itinerary' && (
            <div className="space-y-6">
              {/* Day Tabs Selector */}
              {itinerary && itinerary.days.length > 0 && (
                <div className="flex items-center gap-3 overflow-x-auto pb-2 border-b border-slate-200/80 no-scrollbar">
                  {itinerary.days.map((day, idx) => {
                    const isActive = idx === activeDayIdx;
                    return (
                      <button
                        key={idx}
                        onClick={() => setActiveDayIdx(idx)}
                        className={`px-5 py-2.5 rounded-2xl font-bold text-sm transition-all whitespace-nowrap flex items-center gap-2 border ${
                          isActive
                            ? 'bg-cyan-600 text-white border-cyan-600 shadow-md'
                            : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                        }`}
                      >
                        <CalendarDays className="w-4 h-4" />
                        <span>Day {day.day_number}</span>
                        <span className="text-xs font-normal opacity-90">({day.date})</span>
                      </button>
                    );
                  })}
                </div>
              )}

              {/* Active Day Banner */}
              {currentDay && (
                <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-bold text-slate-900">
                      {currentDay.theme || `Day ${currentDay.day_number} Plan`}
                    </h3>
                    <p className="text-xs font-medium text-slate-500 mt-1">
                      Forecast: <span className="text-cyan-700 font-bold">{currentDay.weather_summary || 'Clear'}</span>
                    </p>
                  </div>
                  <span className="px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-bold border border-slate-200">
                    {currentDay.activities.length} Scheduled Spots
                  </span>
                </div>
              )}

              {/* Activity Cards List for the Selected Day */}
              <div className="space-y-4">
                {currentDay && currentDay.activities.length > 0 ? (
                  currentDay.activities.map((act, idx) => (
                    <ActivityCard key={idx} activity={act} currency="₹" />
                  ))
                ) : (
                  <div className="p-12 text-center text-slate-500 rounded-3xl bg-white border border-slate-200 shadow-xs">
                    No activities for this day. Click "Re-plan Itinerary" to generate.
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'Cuisine' && (
            <div className="space-y-4">
              <h3 className="font-bold text-lg text-slate-900">Top Rated Local Dishes in {trip?.destination}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">
                  <h4 className="font-bold text-base text-slate-900">1. Puneri / Bombay Special Misal Pav</h4>
                  <p className="text-xs text-slate-600 mt-1">Spicy sprouted bean curry topped with farsan & pav.</p>
                  <span className="mt-3 inline-block font-bold text-xs text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200">₹90 - ₹140</span>
                </div>
                <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">
                  <h4 className="font-bold text-base text-slate-900">2. Irani Bun Maska & Special Chai</h4>
                  <p className="text-xs text-slate-600 mt-1">Freshly baked soft bun slathered with salted butter.</p>
                  <span className="mt-3 inline-block font-bold text-xs text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200">₹60 - ₹110</span>
                </div>
                <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">
                  <h4 className="font-bold text-base text-slate-900">3. Maharashtrian Royal Thali</h4>
                  <p className="text-xs text-slate-600 mt-1">Puran Poli, Katachi Amti, Kothimbir Vadi, Solkadhi.</p>
                  <span className="mt-3 inline-block font-bold text-xs text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200">₹250 - ₹450</span>
                </div>
                <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">
                  <h4 className="font-bold text-base text-slate-900">4. Mango / Dryfruit Mastani Shake</h4>
                  <p className="text-xs text-slate-600 mt-1">Thick dessert milkshake topped with ice cream scoops.</p>
                  <span className="mt-3 inline-block font-bold text-xs text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200">₹120 - ₹180</span>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'Transportation' && (
            <div className="space-y-4">
              <h3 className="font-bold text-lg text-slate-900">Local Bus, Metro & Transit Options</h3>
              <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-start gap-3">
                  <Bus className="w-5 h-5 text-cyan-600 mt-0.5 shrink-0" />
                  <div>
                    <h4 className="font-bold text-sm text-slate-900">PMPL City Bus Services</h4>
                    <p className="text-xs text-slate-600 mt-0.5">Route 139 / 139A: Swargate ⇄ Hadapsar ⇄ Shaniwar Wada (Fare: ₹15 - ₹25).</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 border-t border-slate-100 pt-4">
                  <Clock className="w-5 h-5 text-emerald-600 mt-0.5 shrink-0" />
                  <div>
                    <h4 className="font-bold text-sm text-slate-900">Metro Rail Lines</h4>
                    <p className="text-xs text-slate-600 mt-0.5">Purple Line (PCMC ⇄ Swargate) & Aqua Line (Vanaz ⇄ Ramwadi) (Fare: ₹10 - ₹35).</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'Bookings' && (
            <div className="space-y-4">
              <h3 className="font-bold text-lg text-slate-900">PGs & Hotel Bookings</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between">
                  <div>
                    <h4 className="font-bold text-base text-slate-900">Stanza Living / Zolo Stays PG</h4>
                    <p className="text-xs text-slate-600 mt-1">Fully furnished co-living near Hadapsar & Kharadi.</p>
                    <span className="mt-2 block text-xs font-bold text-slate-900">₹6,500 - ₹12,000 / month</span>
                  </div>
                  <a href="https://www.stanzaliving.com/" target="_blank" rel="noreferrer" className="mt-4 text-xs font-bold text-white bg-cyan-600 hover:bg-cyan-700 px-4 py-2 rounded-xl text-center shadow-xs">
                    Book Direct on Stanza Living ↗
                  </a>
                </div>

                <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between">
                  <div>
                    <h4 className="font-bold text-base text-slate-900">Treebo / FabHotels Boutique</h4>
                    <p className="text-xs text-slate-600 mt-1">3-Star Hotel in Central City Square.</p>
                    <span className="mt-2 block text-xs font-bold text-slate-900">₹1,800 / night</span>
                  </div>
                  <a href="https://www.makemytrip.com/hotels/" target="_blank" rel="noreferrer" className="mt-4 text-xs font-bold text-white bg-cyan-600 hover:bg-cyan-700 px-4 py-2 rounded-xl text-center shadow-xs">
                    Book Direct on MakeMyTrip ↗
                  </a>
                </div>
              </div>
            </div>
          )}

        </main>
      </div>
    </div>
  );
};
