import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { PlanningStepper } from '../components/PlanningStepper';
import { tripService } from '../services/api';
import { Trip } from '../types';

export const AIPlanningScreen: React.FC = () => {
  const { tripId } = useParams<{ tripId: string }>();
  const navigate = useNavigate();
  const [trip, setTrip] = useState<Trip | null>(null);

  useEffect(() => {
    if (tripId) {
      tripService.getTrip(parseInt(tripId))
        .then((t) => {
          setTrip(t);
          // Trigger backend planning in parallel
          return tripService.planTrip(parseInt(tripId));
        })
        .catch((err) => console.error('Planning error:', err));
    }
  }, [tripId]);

  const handleComplete = () => {
    if (tripId) {
      navigate(`/dashboard/${tripId}`);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col justify-between">
      <Navbar />

      <div className="flex-1 flex items-center justify-center p-4 py-12">
        <PlanningStepper
          onComplete={handleComplete}
          destination={trip?.destination || 'Destination'}
        />
      </div>
    </div>
  );
};
