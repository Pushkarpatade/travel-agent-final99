import React, { useState } from 'react';
import { AlertTriangle, CloudRain, ShieldAlert, CheckCircle2, RefreshCw, XCircle } from 'lucide-react';
import { Disruption } from '../types';

interface DisruptionCardProps {
  disruption: Disruption;
  onHandle: (disruptionId: number, action: string) => Promise<void>;
}

export const DisruptionCard: React.FC<DisruptionCardProps> = ({ disruption, onHandle }) => {
  const [loading, setLoading] = useState(false);

  const isResolved = disruption.status === 'resolved';

  const getIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'weather':
      case 'weather_conflict':
        return <CloudRain className="w-5 h-5 text-amber-600" />;
      case 'cancellation':
        return <ShieldAlert className="w-5 h-5 text-rose-600" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-cyan-600" />;
    }
  };

  const handleAction = async (action: string) => {
    setLoading(true);
    try {
      await onHandle(disruption.id, action);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`p-5 rounded-2xl border transition-all ${
      isResolved
        ? 'bg-slate-50 border-slate-200 text-slate-500'
        : 'bg-white border-amber-200 shadow-sm'
    }`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3.5">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 border ${
            isResolved
              ? 'bg-slate-100 border-slate-200 text-slate-400'
              : 'bg-amber-50 border-amber-200 text-amber-700'
          }`}>
            {getIcon(disruption.disruption_type)}
          </div>

          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="font-bold text-base text-slate-900">{disruption.title}</h4>
              <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider border ${
                isResolved
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : 'bg-amber-100 text-amber-800 border-amber-200'
              }`}>
                {isResolved ? 'Resolved' : 'Active Disruption'}
              </span>
            </div>

            <p className="text-sm text-slate-600 mt-1">{disruption.description}</p>

            {/* Explanation Reason Badge */}
            {disruption.description.includes('Reason:') && (
              <div className="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-100 border border-slate-200 text-slate-700 text-xs font-semibold">
                <span className="w-2 h-2 rounded-full bg-cyan-500"></span>
                <span>{disruption.description.split('Reason:')[1]}</span>
              </div>
            )}

            {disruption.affected_date && (
              <span className="text-xs text-slate-500 block mt-2 font-medium">
                Affected Date: <strong className="text-slate-800">{disruption.affected_date}</strong>
              </span>
            )}
          </div>
        </div>

        {/* Action Controls */}
        {!isResolved ? (
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => handleAction('auto_replan')}
              disabled={loading}
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs shadow-xs transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Auto Re-plan</span>
            </button>

            <button
              onClick={() => handleAction('ignore')}
              disabled={loading}
              className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
              title="Dismiss"
            >
              <XCircle className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <span className="flex items-center gap-1.5 text-xs text-emerald-700 font-bold px-3 py-1.5 rounded-xl bg-emerald-50 border border-emerald-200">
            <CheckCircle2 className="w-4 h-4" /> Fixed
          </span>
        )}
      </div>

      {disruption.resolution_notes && (
        <div className="mt-3 pt-3 border-t border-slate-100 text-xs text-slate-600 font-medium">
          <span className="text-cyan-700 font-bold">Resolution: </span>
          {disruption.resolution_notes}
        </div>
      )}
    </div>
  );
};
