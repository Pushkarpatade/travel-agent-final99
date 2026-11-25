import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  CalendarDays,
  DollarSign,
  MapPin,
  Sparkles,
  AlertTriangle,
  Clock,
  Navigation,
  ArrowRight,
  PieChart,
  MessageSquare,
  PlusCircle,
  CheckCircle2
} from 'lucide-react';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { WeatherWidget } from '../components/WeatherWidget';
import { ActivityCard } from '../components/ActivityCard';
import { DisruptionCard } from '../components/DisruptionCard';
import { tripService } from '../services/api';
import { Trip, Itinerary, BudgetBreakdown, Disruption, WeatherData } from '../types';

export const DashboardPage: React.FC = () => {
  const { tripId } = useParams<{ tripId: string }>();
  const navigate = useNavigate();

  const [trips, setTrips] = useState<Trip[]>([]);
  const [activeTrip, setActiveTrip] = useState<Trip | null>(null);
  const [itinerary, setItinerary] = useState<Itinerary | null>(null);
  const [budget, setBudget] = useState<BudgetBreakdown | null>(null);
  const [disruptions, setDisruptions] = useState<Disruption[]>([]);
  const [weather, setWeather] = useState<WeatherData | undefined>(undefined);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    tripService.listTrips()
      .then((data) => {
        setTrips(data);
        if (data.length > 0) {
          const selectedId = tripId ? parseInt(tripId) : data[data.length - 1].id;
          const current = data.find((t) => t.id === selectedId) || data[data.length - 1];
          setActiveTrip(current);
          loadTripDetails(current);
        } else {
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [tripId]);

  const loadTripDetails = async (t: Trip) => {
    setLoading(true);
    try {
      const [itinData, budData, disData, weathData] = await Promise.allSettled([
        tripService.getItinerary(t.id),
        tripService.getBudget(t.id),
        tripService.getDisruptions(t.id),
        tripService.getWeather(t.destination)
      ]);

      if (itinData.status === 'fulfilled') setItinerary(itinData.value);
      if (budData.status === 'fulfilled') setBudget(budData.value);
      if (disData.status === 'fulfilled') setDisruptions(disData.value);
      if (weathData.status === 'fulfilled') setWeather(weathData.value);
    } finally {
      setLoading(false);
    }
  };

  const handleDisruptionAction = async (disruptionId: number, action: string) => {
    if (activeTrip) {
      const res = await tripService.handleDisruption(activeTrip.id, disruptionId, action);
      if (res.updated_itinerary) {
        setItinerary(res.updated_itinerary);
      }
      const updatedDis = await tripService.getDisruptions(activeTrip.id);
      setDisruptions(updatedDis);
    }
  };

  if (!activeTrip && !loading && trips.length === 0) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
        <Navbar />
        <div className="flex-1 flex items-center justify-center p-4">
          <div className="text-center max-w-md p-8 rounded-3xl bg-white border border-slate-200 shadow-sm">
            <Sparkles className="w-12 h-12 text-cyan-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-slate-900 mb-2">No Active Trips Found</h2>
            <p className="text-sm text-slate-500 mb-6">Start by creating your first AI-planned trip itinerary.</p>
            <Link
              to="/create-trip"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-sm shadow-sm"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Create New Trip</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const activeDisruptionsCount = disruptions.filter((d) => d.status === 'active').length;
  const todayDay = itinerary?.days[0];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <Navbar />

      <div className="flex-1 flex flex-col md:flex-row">
        {activeTrip && <Sidebar tripId={activeTrip.id} destination={activeTrip.destination} />}

        <main className="flex-1 p-4 sm:p-6 md:p-8 space-y-6 sm:space-y-8 max-w-7xl">
          {activeTrip && (
            <>
              {/* Top Banner Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs flex items-center justify-between">
                  <div>
                    <span className="text-xs text-slate-500 font-semibold">Destination</span>
                    <h3 className="text-xl font-bold text-slate-900 capitalize mt-0.5">{activeTrip.destination}</h3>
                  </div>
                  <div className="w-10 h-10 rounded-xl bg-cyan-50 border border-cyan-200 flex items-center justify-center text-cyan-700">
                    <MapPin className="w-5 h-5" />
                  </div>
                </div>

                <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs flex items-center justify-between">
                  <div>
                    <span className="text-xs text-slate-500 font-semibold">Dates & Style</span>
                    <h3 className="text-sm font-bold text-slate-900 mt-0.5">{activeTrip.start_date} to {activeTrip.end_date}</h3>
                    <span className="text-[11px] text-cyan-700 font-bold">{activeTrip.travel_style} Style</span>
                  </div>
                  <div className="w-10 h-10 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-700">
                    <CalendarDays className="w-5 h-5" />
                  </div>
                </div>

                <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs flex items-center justify-between">
                  <div>
                    <span className="text-xs text-slate-500 font-semibold">Total Budget</span>
                    <h3 className="text-xl font-bold text-emerald-700 mt-0.5">₹{activeTrip.budget.toFixed(0)}</h3>
                    {budget && (
                      <span className="text-[11px] text-slate-500">Est. Cost: ₹{budget.estimated_total_cost.toFixed(0)}</span>
                    )}
                  </div>
                  <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700">
                    <DollarSign className="w-5 h-5" />
                  </div>
                </div>

                <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs flex items-center justify-between">
                  <div>
                    <span className="text-xs text-slate-500 font-semibold">Disruption Alerts</span>
                    <h3 className="text-xl font-bold text-slate-900 mt-0.5">
                      {activeDisruptionsCount > 0 ? (
                        <span className="text-amber-600 flex items-center gap-1 font-bold">
                          <AlertTriangle className="w-4 h-4" /> {activeDisruptionsCount} Active
                        </span>
                      ) : (
                        <span className="text-emerald-600 flex items-center gap-1 font-bold">
                          <CheckCircle2 className="w-4 h-4" /> All Clear
                        </span>
                      )}
                    </h3>
                  </div>
                  <div className={`w-10 h-10 rounded-xl border flex items-center justify-center ${
                    activeDisruptionsCount > 0 ? 'bg-amber-50 border-amber-200 text-amber-700' : 'bg-slate-100 border-slate-200 text-slate-500'
                  }`}>
                    <AlertTriangle className="w-5 h-5" />
                  </div>
                </div>
              </div>

              {/* Weather Widget */}
              <WeatherWidget weather={weather} />

              {/* Active Disruptions Notification Card */}
              {activeDisruptionsCount > 0 && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-base font-bold text-amber-700 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" /> Active Disruptions Detected
                    </h3>
                    <Link to={`/disruptions/${activeTrip.id}`} className="text-xs font-bold text-cyan-700 hover:underline">
                      View Disruption Center →
                    </Link>
                  </div>
                  {disruptions.filter((d) => d.status === 'active').map((dis) => (
                    <DisruptionCard key={dis.id} disruption={dis} onHandle={handleDisruptionAction} />
                  ))}
                </div>
              )}

              {/* Today's Schedule Overview */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-slate-900">Today's Schedule</h3>
                    <p className="text-xs font-medium text-slate-500">
                      {todayDay ? `Day 1 (${todayDay.date}) - ${todayDay.theme || 'Exploration'}` : 'Itinerary overview'}
                    </p>
                  </div>

                  <Link
                    to={`/itinerary/${activeTrip.id}`}
                    className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-white border border-slate-200 text-xs text-cyan-700 font-bold hover:bg-slate-50 transition-colors shadow-xs"
                  >
                    <span>View Full Day-by-Day Plan</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>

                <div className="space-y-3">
                  {todayDay && todayDay.activities.length > 0 ? (
                    todayDay.activities.map((act, idx) => (
                      <ActivityCard key={idx} activity={act} currency="₹" />
                    ))
                  ) : (
                    <div className="p-8 rounded-2xl bg-white border border-slate-200 text-center text-sm text-slate-500">
                      No activities generated for today.
                    </div>
                  )}
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
};
