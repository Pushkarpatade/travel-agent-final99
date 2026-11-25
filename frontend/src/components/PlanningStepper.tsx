import React, { useEffect, useState } from 'react';
import { Search, CloudSun, MapPin, Calculator, Calendar, CheckCircle2, Loader2, Sparkles } from 'lucide-react';

interface PlanningStepperProps {
  onComplete: () => void;
  destination: string;
}

export const PlanningStepper: React.FC<PlanningStepperProps> = ({ onComplete, destination }) => {
  const steps = [
    { label: 'Understand User Requirements', detail: `Parsing style & interests for ${destination}...`, icon: Sparkles },
    { label: 'Search Attractions & Dining', detail: 'Executing Tavily web search for top spots...', icon: Search },
    { label: 'Check Weather Forecast', detail: 'Evaluating rain risks and outdoor suitability...', icon: CloudSun },
    { label: 'Calculate Travel Times & Distance', detail: 'Geocoding locations & organizing clusters...', icon: MapPin },
    { label: 'Calculate & Optimize Budget (₹)', detail: 'Allocating funds across stays, dining, transport...', icon: Calculator },
    { label: 'Build & Validate Itinerary', detail: 'Checking opening hours & schedule overlaps...', icon: Calendar },
    { label: 'Finalize Custom Itinerary', detail: 'Writing day-by-day itinerary to database...', icon: CheckCircle2 },
  ];

  const [currentStep, setCurrentStep] = useState<number>(0);

  useEffect(() => {
    if (currentStep < steps.length - 1) {
      const timer = setTimeout(() => {
        setCurrentStep((prev) => prev + 1);
      }, 1200);
      return () => clearTimeout(timer);
    } else {
      const finishTimer = setTimeout(() => {
        onComplete();
      }, 1000);
      return () => clearTimeout(finishTimer);
    }
  }, [currentStep]);

  return (
    <div className="max-w-2xl mx-auto p-8 rounded-3xl bg-white border border-slate-200 shadow-xl">
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-cyan-100 border border-cyan-200 text-cyan-800 text-xs font-bold uppercase tracking-wider mb-3">
          <Sparkles className="w-3.5 h-3.5 text-cyan-600" />
          LangGraph Planning Workflow
        </div>
        <h2 className="text-2xl font-bold text-slate-900 capitalize">Synthesizing Trip to {destination}</h2>
        <p className="text-sm font-medium text-slate-500 mt-1">
          TravelPilot multi-agent engine is searching live data and crafting your optimal itinerary.
        </p>
      </div>

      <div className="space-y-4">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          const isDone = idx < currentStep;
          const isCurrent = idx === currentStep;

          return (
            <div
              key={idx}
              className={`p-4 rounded-2xl border transition-all flex items-center justify-between gap-4 ${
                isDone
                  ? 'bg-slate-50 border-slate-200 text-slate-700'
                  : isCurrent
                  ? 'bg-cyan-50 border-cyan-300 text-cyan-900 shadow-sm scale-[1.01]'
                  : 'bg-slate-50/50 border-slate-100 text-slate-400 opacity-60'
              }`}
            >
              <div className="flex items-center gap-4">
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 border font-bold ${
                    isDone
                      ? 'bg-emerald-100 border-emerald-300 text-emerald-700'
                      : isCurrent
                      ? 'bg-cyan-600 text-white border-cyan-600 shadow-xs'
                      : 'bg-white border-slate-200 text-slate-400'
                  }`}
                >
                  {isDone ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-700" />
                  ) : isCurrent ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Icon className="w-5 h-5" />
                  )}
                </div>

                <div>
                  <h4 className="font-bold text-sm text-slate-900">{step.label}</h4>
                  <p className="text-xs font-medium text-slate-500 mt-0.5">{step.detail}</p>
                </div>
              </div>

              {isDone && (
                <span className="text-xs font-bold text-emerald-700 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200">
                  Complete
                </span>
              )}
              {isCurrent && (
                <span className="text-xs font-bold text-cyan-800 px-2.5 py-1 rounded-full bg-cyan-100 border border-cyan-200 animate-pulse">
                  Processing...
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
