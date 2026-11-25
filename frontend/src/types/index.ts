export interface User {
  id: number;
  email: string;
  full_name: string;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

export interface Trip {
  id: number;
  user_id: number;
  destination: string;
  start_date: string;
  end_date: string;
  budget: number;
  currency: string;
  travelers: number;
  travel_style: string;
  interests: string[];
  food_preferences: string;
  accommodation_preference: string;
  transportation_preference: string;
  activity_intensity: string;
  status: string;
  created_at: string;
}

export interface TripFormData {
  destination: string;
  start_date: string;
  end_date: string;
  budget: number;
  currency: string;
  travelers: number;
  travel_style: string;
  interests: string[];
  food_preferences: string;
  accommodation_preference: string;
  transportation_preference: string;
  activity_intensity: string;
}

export interface Activity {
  id?: number;
  name: string;
  description?: string;
  category: string;
  location_name?: string;
  latitude?: number;
  longitude?: number;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  estimated_cost: number;
  opening_hours: string;
  travel_time_from_prev_mins: number;
  distance_from_prev_km: number;
  backup_option?: string;
  is_cancelled?: boolean;
  notes?: string;
}

export interface ItineraryDay {
  id?: number;
  day_number: number;
  date: string;
  theme?: string;
  weather_summary?: string;
  activities: Activity[];
}

export interface Itinerary {
  id: number;
  trip_id: number;
  version: number;
  is_active: boolean;
  total_estimated_cost: number;
  summary?: string;
  days: ItineraryDay[];
  created_at: string;
}

export interface BudgetBreakdown {
  total_budget: number;
  currency: string;
  estimated_total_cost: number;
  remaining_budget: number;
  accommodation: number;
  dining: number;
  transportation: number;
  activities: number;
  miscellaneous: number;
  category_percentages: Record<string, number>;
}

export interface Disruption {
  id: number;
  trip_id: number;
  disruption_type: string;
  title: string;
  description: string;
  affected_date?: string;
  status: string;
  resolution_notes?: string;
  created_at: string;
}

export interface ChatMessage {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface WeatherDay {
  date: string;
  condition: string;
  temp_high_c: number;
  temp_low_c: number;
  rain_probability_pct: number;
  wind_kmh: number;
  icon: string;
}

export interface WeatherData {
  destination: string;
  forecast: WeatherDay[];
}
