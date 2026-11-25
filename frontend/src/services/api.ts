import axios from 'axios';
import {
  Trip,
  TripFormData,
  Itinerary,
  BudgetBreakdown,
  Disruption,
  ChatMessage,
  WeatherData
} from '../types';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add Auth Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('tp_auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  register: async (email: string, password: string, fullName: string) => {
    const res = await api.post('/auth/register', { email, password, full_name: fullName });
    return res.data;
  },
  login: async (email: string, password: string) => {
    const res = await api.post('/auth/login', { email, password });
    return res.data;
  },
  sendOtp: async (email: string) => {
    const res = await api.post('/auth/send-otp', { email });
    return res.data;
  },
  verifyOtp: async (email: string, otp: string, fullName?: string, password?: string) => {
    const res = await api.post('/auth/verify-otp', { email, otp, full_name: fullName, password });
    return res.data;
  },
  firebaseLogin: async (email: string, fullName: string) => {
    const res = await api.post('/auth/firebase-login', { email, full_name: fullName });
    return res.data;
  },
  getMe: async () => {
    const res = await api.get('/auth/me');
    return res.data;
  },
};

export const tripService = {
  createTrip: async (data: TripFormData): Promise<Trip> => {
    const res = await api.post('/trips', data);
    return res.data;
  },
  listTrips: async (): Promise<Trip[]> => {
    const res = await api.get('/trips');
    return res.data;
  },
  getTrip: async (tripId: number): Promise<Trip> => {
    const res = await api.get(`/trips/${tripId}`);
    return res.data;
  },
  planTrip: async (tripId: number): Promise<Itinerary> => {
    const res = await api.post(`/trips/${tripId}/plan`);
    return res.data;
  },
  replanTrip: async (tripId: number): Promise<Itinerary> => {
    const res = await api.post(`/trips/${tripId}/replan`);
    return res.data;
  },
  getItinerary: async (tripId: number): Promise<Itinerary> => {
    const res = await api.get(`/trips/${tripId}/itinerary`);
    return res.data;
  },
  getBudget: async (tripId: number): Promise<BudgetBreakdown> => {
    const res = await api.get(`/trips/${tripId}/budget`);
    return res.data;
  },
  getDisruptions: async (tripId: number): Promise<Disruption[]> => {
    const res = await api.get(`/trips/${tripId}/disruptions`);
    return res.data;
  },
  handleDisruption: async (tripId: number, disruptionId: number, action: string) => {
    const res = await api.post(`/trips/${tripId}/handle-disruption`, {
      disruption_id: disruptionId,
      action
    });
    return res.data;
  },
  sendChat: async (tripId: number, message: string): Promise<{ reply: string; suggested_actions: string[]; updated_itinerary?: Itinerary }> => {
    const res = await api.post('/chat', { trip_id: tripId, message });
    return res.data;
  },
  getWeather: async (destination: string): Promise<WeatherData> => {
    const res = await api.get('/weather', { params: { destination } });
    return res.data;
  }
};
