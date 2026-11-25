import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { MapPin, Navigation, Compass, ExternalLink } from 'lucide-react';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { tripService } from '../services/api';
import { Trip, Itinerary, Activity } from '../types';

export const MapViewPage: React.FC = () => {
  const { tripId } = useParams<{ tripId: string }>();

  const [trip, setTrip] = useState<Trip | null>(null);
  const [itinerary, setItinerary] = useState<Itinerary | null>(null);
  const [selectedActivity, setSelectedActivity] = useState<Activity | null>(null);

  useEffect(() => {
    if (tripId) {
      const id = parseInt(tripId);
      Promise.all([tripService.getTrip(id), tripService.getItinerary(id)])
        .then(([t, itin]) => {
          setTrip(t);
          setItinerary(itin);
          if (itin.days.length > 0 && itin.days[0].activities.length > 0) {
            setSelectedActivity(itin.days[0].activities[0]);
          }
        });
    }
  }, [tripId]);

  const allActivities: { dayNum: number; activity: Activity }[] = [];
  if (itinerary) {
    itinerary.days.forEach((day) => {
      day.activities.forEach((act) => {
        allActivities.push({ dayNum: day.day_number, activity: act });
      });
    });
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <Navbar />

      <div className="flex-1 flex flex-col md:flex-row">
        {trip && <Sidebar tripId={trip.id} destination={trip.destination} />}

        <main className="flex-1 p-4 sm:p-6 md:p-8 space-y-6 max-w-7xl">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Spatial Map & Route Explorer</h1>
            <p className="text-xs font-semibold text-slate-500 mt-1">
              Geocoded activity pins, transit vectors, and distance matrices for {trip?.destination}.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-[500px] lg:h-[650px]">
            
            {/* Interactive Location Marker List Sidebar */}
            <div className="lg:col-span-1 p-4 rounded-3xl bg-white border border-slate-200 shadow-sm flex flex-col h-full overflow-hidden">
              <h3 className="font-bold text-sm text-slate-900 mb-3 px-2 flex items-center gap-2">
                <MapPin className="w-4 h-4 text-cyan-600" />
                <span>All Scheduled Pins ({allActivities.length})</span>
              </h3>

              <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
                {allActivities.map((item, idx) => {
                  const act = item.activity;
                  const isSelected = selectedActivity?.name === act.name;

                  return (
                    <div
                      key={idx}
                      onClick={() => setSelectedActivity(act)}
                      className={`p-3.5 rounded-2xl border cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-cyan-50 border-cyan-300 text-cyan-900 shadow-xs'
                          : 'bg-slate-50 border-slate-200 hover:border-slate-300 text-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between text-xs font-bold mb-1">
                        <span className="px-2 py-0.5 rounded-md bg-white text-cyan-700 border border-slate-200">
                          Day {item.dayNum} • {act.start_time}
                        </span>
                        <span className="text-slate-500 font-semibold">{act.category}</span>
                      </div>

                      <h4 className="font-bold text-sm text-slate-900">{act.name}</h4>

                      {act.location_name && (
                        <p className="text-xs text-slate-500 font-medium mt-1 flex items-center gap-1">
                          <MapPin className="w-3 h-3 text-slate-400 shrink-0" />
                          <span className="truncate">{act.location_name}</span>
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Map Visualizer Mockup */}
            <div className="lg:col-span-2 rounded-3xl bg-white border border-slate-200 p-6 flex flex-col justify-between relative overflow-hidden shadow-sm">
              <div className="relative z-10 flex items-center justify-between bg-slate-50 p-4 rounded-2xl border border-slate-200">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-cyan-100 border border-cyan-200 flex items-center justify-center text-cyan-700">
                    <Compass className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-sm text-slate-900">
                      {selectedActivity ? selectedActivity.name : `Central ${trip?.destination} Map`}
                    </h3>
                    <span className="text-xs font-medium text-slate-500">
                      Coords: {selectedActivity?.latitude || 18.5204}, {selectedActivity?.longitude || 73.8567}
                    </span>
                  </div>
                </div>

                {selectedActivity && (
                  <a
                    href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(selectedActivity.name + ' ' + (trip?.destination || ''))}`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs shadow-xs"
                  >
                    <span>Google Maps</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>

              <div className="my-auto py-12 flex flex-col items-center justify-center text-center relative z-10">
                <div className="w-20 h-20 rounded-full bg-cyan-100 border-2 border-cyan-300 flex items-center justify-center text-cyan-700 shadow-sm mb-4">
                  <MapPin className="w-10 h-10" />
                </div>

                <h2 className="text-xl font-bold text-slate-900 max-w-md">
                  {selectedActivity ? selectedActivity.name : 'Select a pin to view spatial transit breakdown'}
                </h2>

                {selectedActivity && (
                  <div className="mt-4 p-4 rounded-2xl bg-slate-50 border border-slate-200 text-xs text-slate-700 max-w-lg space-y-2">
                    <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                      <span className="text-slate-500">Estimated Transit:</span>
                      <strong className="text-cyan-700 font-bold">{selectedActivity.travel_time_from_prev_mins} mins ({selectedActivity.distance_from_prev_km} km)</strong>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">Opening Hours:</span>
                      <strong className="text-slate-900 font-bold">{selectedActivity.opening_hours}</strong>
                    </div>
                  </div>
                )}
              </div>
            </div>

          </div>
        </main>
      </div>
    </div>
  );
};
