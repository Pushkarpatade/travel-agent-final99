import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { ChatWidget } from '../components/ChatWidget';
import { tripService } from '../services/api';
import { Trip } from '../types';

export const ChatAssistantPage: React.FC = () => {
  const { tripId } = useParams<{ tripId: string }>();
  const [trip, setTrip] = useState<Trip | null>(null);

  useEffect(() => {
    if (tripId) {
      tripService.getTrip(parseInt(tripId))
        .then((t) => setTrip(t))
        .catch((err) => console.error(err));
    }
  }, [tripId]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <Navbar />

      <div className="flex-1 flex flex-col md:flex-row">
        {trip && <Sidebar tripId={trip.id} destination={trip.destination} />}

        <main className="flex-1 p-4 sm:p-6 md:p-8 max-w-5xl">
          <div className="mb-6">
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900">AI Travel Assistant Chat</h1>
            <p className="text-xs text-slate-500 mt-1">
              Natural language command interface for schedule updates, morning plan queries, and budget modifications.
            </p>
          </div>

          {trip && <ChatWidget tripId={trip.id} destination={trip.destination} />}
        </main>
      </div>
    </div>
  );
};
