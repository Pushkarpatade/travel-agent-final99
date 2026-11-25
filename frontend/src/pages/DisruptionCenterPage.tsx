import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { AlertTriangle, ShieldAlert, RefreshCw, CheckCircle2 } from 'lucide-react';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { DisruptionCard } from '../components/DisruptionCard';
import { tripService } from '../services/api';
import { Trip, Disruption } from '../types';

export const DisruptionCenterPage: React.FC = () => {
  const { tripId } = useParams<{ tripId: string }>();

  const [trip, setTrip] = useState<Trip | null>(null);
  const [disruptions, setDisruptions] = useState<Disruption[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [replanning, setReplanning] = useState<boolean>(false);

  useEffect(() => {
    if (tripId) {
      const id = parseInt(tripId);
      Promise.all([tripService.getTrip(id), tripService.getDisruptions(id)])
        .then(([t, dis]) => {
          setTrip(t);
          setDisruptions(dis);
        })
        .finally(() => setLoading(false));
    }
  }, [tripId]);

  const handleHandleAction = async (disruptionId: number, action: string) => {
    if (!tripId) return;
    await tripService.handleDisruption(parseInt(tripId), disruptionId, action);
    const updated = await tripService.getDisruptions(parseInt(tripId));
    setDisruptions(updated);
  };

  const handleGlobalReplan = async () => {
    if (!tripId) return;
    setReplanning(true);
    try {
      await tripService.replanTrip(parseInt(tripId));
      const updated = await tripService.getDisruptions(parseInt(tripId));
      setDisruptions(updated);
    } finally {
      setReplanning(false);
    }
  };

  const activeDisruptions = disruptions.filter((d) => d.status === 'active');
  const resolvedDisruptions = disruptions.filter((d) => d.status === 'resolved');

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <Navbar />

      <div className="flex-1 flex">
        {trip && <Sidebar tripId={trip.id} destination={trip.destination} />}

        <main className="flex-1 p-6 md:p-8 space-y-6 max-w-5xl">
          <div className="flex items-center justify-between flex-wrap gap-4 pb-6 border-b border-slate-200">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-100 border border-amber-200 text-amber-800 text-xs font-bold uppercase tracking-wider mb-2">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                Real-Time Risk & Schedule Shield
              </div>
              <h1 className="text-2xl font-bold text-slate-900">Disruption Management Center</h1>
              <p className="text-xs text-slate-500 font-medium mt-0.5">
                Automated weather rain detection, opening hours validation, and activity replacements.
              </p>
            </div>

            <button
              onClick={handleGlobalReplan}
              disabled={replanning}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs shadow-sm transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${replanning ? 'animate-spin' : ''}`} />
              <span>Auto Re-plan Entire Trip</span>
            </button>
          </div>

          <div className="space-y-4">
            <h3 className="font-bold text-base text-slate-800 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-600" />
              <span>Active Alerts ({activeDisruptions.length})</span>
            </h3>

            {activeDisruptions.length > 0 ? (
              activeDisruptions.map((dis) => (
                <DisruptionCard key={dis.id} disruption={dis} onHandle={handleHandleAction} />
              ))
            ) : (
              <div className="p-8 rounded-3xl bg-white border border-slate-200 text-center text-sm text-slate-500 shadow-xs">
                <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
                <span>No active schedule disruptions detected for this trip!</span>
              </div>
            )}
          </div>

          {resolvedDisruptions.length > 0 && (
            <div className="space-y-4 pt-6">
              <h3 className="font-bold text-base text-slate-500">Resolved History ({resolvedDisruptions.length})</h3>
              {resolvedDisruptions.map((dis) => (
                <DisruptionCard key={dis.id} disruption={dis} onHandle={handleHandleAction} />
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};
