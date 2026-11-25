import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { DollarSign, PieChart as PieIcon, BarChart3 } from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip
} from 'recharts';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { tripService } from '../services/api';
import { Trip, BudgetBreakdown } from '../types';

export const BudgetPage: React.FC = () => {
  const { tripId } = useParams<{ tripId: string }>();

  const [trip, setTrip] = useState<Trip | null>(null);
  const [budget, setBudget] = useState<BudgetBreakdown | null>(null);

  useEffect(() => {
    if (tripId) {
      const id = parseInt(tripId);
      Promise.all([tripService.getTrip(id), tripService.getBudget(id)])
        .then(([t, b]) => {
          setTrip(t);
          setBudget(b);
        });
    }
  }, [tripId]);

  const COLORS = ['#0284c7', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

  const chartData = budget ? [
    { name: 'Accommodation', amount: budget.accommodation },
    { name: 'Dining', amount: budget.dining },
    { name: 'Activities', amount: budget.activities },
    { name: 'Transport', amount: budget.transportation },
    { name: 'Misc', amount: budget.miscellaneous },
  ] : [];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <Navbar />

      <div className="flex-1 flex flex-col md:flex-row">
        {trip && <Sidebar tripId={trip.id} destination={trip.destination} />}

        <main className="flex-1 p-4 sm:p-6 md:p-8 space-y-6 max-w-7xl">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Financial & Budget Optimizer</h1>
            <p className="text-xs font-semibold text-slate-500 mt-1">
              Category allocation charts and live spending breakdown for {trip?.destination}.
            </p>
          </div>

          {budget && (
            <>
              {/* Stat Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs">
                  <span className="text-xs text-slate-500 font-semibold">Target Budget</span>
                  <h3 className="text-2xl font-bold text-slate-900 mt-1">₹{budget.total_budget.toFixed(0)}</h3>
                </div>

                <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs">
                  <span className="text-xs text-slate-500 font-semibold">Estimated Total Cost</span>
                  <h3 className="text-2xl font-bold text-cyan-700 mt-1">₹{budget.estimated_total_cost.toFixed(0)}</h3>
                </div>

                <div className={`p-5 rounded-2xl border shadow-xs ${
                  budget.remaining_budget >= 0 ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800'
                }`}>
                  <span className="text-xs font-bold uppercase opacity-80">Remaining Surplus</span>
                  <h3 className="text-2xl font-bold mt-1">₹{budget.remaining_budget.toFixed(0)}</h3>
                </div>
              </div>

              {/* Recharts Visualizations */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Pie Chart */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between">
                  <h3 className="font-bold text-base text-slate-900 flex items-center gap-2 mb-4">
                    <PieIcon className="w-5 h-5 text-cyan-600" />
                    <span>Category Share Breakdown</span>
                  </h3>

                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={chartData}
                          dataKey="amount"
                          nameKey="name"
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        >
                          {chartData.map((_, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value: number) => `₹${value.toFixed(0)}`} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Bar Chart */}
                <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between">
                  <h3 className="font-bold text-base text-slate-900 flex items-center gap-2 mb-4">
                    <BarChart3 className="w-5 h-5 text-emerald-600" />
                    <span>Category Spending Comparison</span>
                  </h3>

                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData}>
                        <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                        <YAxis stroke="#64748b" fontSize={12} />
                        <Tooltip formatter={(value: number) => `₹${value.toFixed(0)}`} />
                        <Bar dataKey="amount" fill="#0284c7" radius={[6, 6, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
};
