import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  MapPin,
  Calendar,
  Users,
  Sparkles,
  ArrowRight,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { Navbar } from '../components/Navbar';
import { tripService, authService } from '../services/api';
import { TripFormData } from '../types';

export const TripCreationPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const initialDestination = location.state?.destination || '';

  const [formData, setFormData] = useState<TripFormData>({
    destination: initialDestination,
    start_date: '2026-10-01',
    end_date: '2026-10-04',
    budget: 25000,
    currency: 'INR',
    travelers: 2,
    travel_style: 'Balanced',
    interests: ['Culture', 'Food', 'History'],
    food_preferences: 'Local Cuisine & Bistros',
    accommodation_preference: 'Boutique Hotel',
    transportation_preference: 'Public Transit & Walking',
    activity_intensity: 'Moderate'
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const interestOptions = ['Culture', 'Food', 'History', 'Nature', 'Art & Museums', 'Shopping', 'Nightlife', 'Relaxation'];

  const toggleInterest = (interest: string) => {
    setFormData((prev) => {
      const exists = prev.interests.includes(interest);
      return {
        ...prev,
        interests: exists
          ? prev.interests.filter((i) => i !== interest)
          : [...prev.interests, interest]
      };
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.destination.trim() || loading) return;

    setLoading(true);
    setError(null);

    try {
      // Auto-ensure valid auth token
      const currentToken = localStorage.getItem('tp_auth_token');
      if (!currentToken) {
        try {
          const authData = await authService.register(
            `guest_${Date.now()}@travelpilot.ai`,
            'password123',
            'Guest Traveler'
          );
          localStorage.setItem('tp_auth_token', authData.access_token);
          localStorage.setItem('tp_user', JSON.stringify(authData.user));
        } catch {
          const loginData = await authService.login('demo@travelpilot.ai', 'password123');
          localStorage.setItem('tp_auth_token', loginData.access_token);
          localStorage.setItem('tp_user', JSON.stringify(loginData.user));
        }
      }

      const trip = await tripService.createTrip(formData);
      navigate(`/plan-trip/${trip.id}`);
    } catch (err: any) {
      console.error('Trip creation failed:', err);
      // Auto-retry with fresh token
      try {
        const authData = await authService.register(
          `guest_${Date.now()}@travelpilot.ai`,
          'password123',
          'Guest Traveler'
        );
        localStorage.setItem('tp_auth_token', authData.access_token);
        localStorage.setItem('tp_user', JSON.stringify(authData.user));
        const retryTrip = await tripService.createTrip(formData);
        navigate(`/plan-trip/${retryTrip.id}`);
      } catch (retryErr: any) {
        setError('Connection issue. Please verify your backend server is active and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <Navbar />

      <div className="max-w-4xl mx-auto px-4 py-12 flex-1 w-full">
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-cyan-100 border border-cyan-200 text-cyan-800 text-xs font-bold uppercase tracking-wider mb-3 shadow-2xs">
            <Sparkles className="w-3.5 h-3.5 text-cyan-600" />
            AI Travel Parameters
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900">Configure Your AI Trip</h1>
          <p className="text-sm font-medium text-slate-600 mt-1">
            Provide your destination, budget in Rupees (₹), and preferences to prime the LangGraph agent.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-bold flex items-center gap-2 shadow-xs">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="p-8 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-8">
          
          {/* Destination & Dates */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Destination
              </label>
              <div className="relative">
                <MapPin className="w-4 h-4 text-cyan-600 absolute left-3.5 top-3.5" />
                <input
                  type="text"
                  required
                  value={formData.destination}
                  onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
                  placeholder="e.g. Dubai, Mumbai, Pune, Paris"
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-cyan-600 font-semibold"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Start Date
              </label>
              <div className="relative">
                <Calendar className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                <input
                  type="date"
                  required
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-cyan-600 font-semibold"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                End Date
              </label>
              <div className="relative">
                <Calendar className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                <input
                  type="date"
                  required
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-cyan-600 font-semibold"
                />
              </div>
            </div>
          </div>

          {/* Budget & Travelers */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Total Budget (₹ INR)
              </label>
              <div className="relative">
                <span className="text-emerald-700 font-bold absolute left-3.5 top-2.5 text-sm">₹</span>
                <input
                  type="number"
                  required
                  min={1000}
                  step={500}
                  value={formData.budget}
                  onChange={(e) => setFormData({ ...formData, budget: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-cyan-600 font-bold"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Travelers Count
              </label>
              <div className="relative">
                <Users className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                <input
                  type="number"
                  required
                  min={1}
                  max={20}
                  value={formData.travelers}
                  onChange={(e) => setFormData({ ...formData, travelers: parseInt(e.target.value) || 1 })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-cyan-600 font-semibold"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Travel Style
              </label>
              <select
                value={formData.travel_style}
                onChange={(e) => setFormData({ ...formData, travel_style: e.target.value })}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-4 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-cyan-600 font-semibold"
              >
                <option value="Balanced">Balanced (Standard Sightseeing & Food)</option>
                <option value="Luxury">Luxury (Premium Stays & Dining)</option>
                <option value="Budget">Budget / Backpacker</option>
                <option value="Family">Family Friendly</option>
                <option value="Relaxed">Relaxed Pace</option>
              </select>
            </div>
          </div>

          {/* Interests Pills */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
              Select Your Main Interests
            </label>
            <div className="flex flex-wrap gap-2.5">
              {interestOptions.map((interest) => {
                const isSelected = formData.interests.includes(interest);
                return (
                  <button
                    type="button"
                    key={interest}
                    onClick={() => toggleInterest(interest)}
                    className={`px-4 py-2 rounded-xl text-xs font-bold border transition-all ${
                      isSelected
                        ? 'bg-cyan-600 text-white border-cyan-600 shadow-xs'
                        : 'bg-slate-50 text-slate-700 border-slate-300 hover:bg-slate-100'
                    }`}
                  >
                    {interest}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Detailed Preferences */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 border-t border-slate-200">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Food Preference
              </label>
              <input
                type="text"
                value={formData.food_preferences}
                onChange={(e) => setFormData({ ...formData, food_preferences: e.target.value })}
                placeholder="e.g. Local Cuisine, Fine Dining, Vegan"
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-4 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-cyan-600 font-semibold"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Accommodation Preference
              </label>
              <input
                type="text"
                value={formData.accommodation_preference}
                onChange={(e) => setFormData({ ...formData, accommodation_preference: e.target.value })}
                placeholder="e.g. Boutique Hotel, City Center Airbnb"
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-4 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-cyan-600 font-semibold"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Activity Intensity / Pace
              </label>
              <select
                value={formData.activity_intensity}
                onChange={(e) => setFormData({ ...formData, activity_intensity: e.target.value })}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-4 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-cyan-600 font-semibold"
              >
                <option value="Relaxed">Relaxed (1-2 main activities/day)</option>
                <option value="Moderate">Moderate (3-4 balanced activities/day)</option>
                <option value="Packed">Packed / Fast Paced (5+ activities/day)</option>
              </select>
            </div>
          </div>

          {/* Submit */}
          <div className="pt-4 border-t border-slate-200 text-right">
            <button
              type="submit"
              disabled={loading}
              className="px-8 py-3.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-sm disabled:opacity-50 ml-auto"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                  <span>Creating Trip...</span>
                </>
              ) : (
                <>
                  <span>Generate AI Itinerary</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
