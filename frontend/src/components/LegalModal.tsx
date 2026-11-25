import React from 'react';
import { X, Shield, FileText, AlertTriangle, ExternalLink } from 'lucide-react';

interface LegalModalProps {
  isOpen: boolean;
  onClose: () => void;
  type: 'privacy' | 'terms';
}

export const LegalModal: React.FC<LegalModalProps> = ({ isOpen, onClose, type }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-2xl max-h-[85vh] flex flex-col rounded-3xl bg-white border border-slate-200 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-100 border border-cyan-200 flex items-center justify-center text-cyan-700">
              {type === 'privacy' ? <Shield className="w-5 h-5" /> : <FileText className="w-5 h-5" />}
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900">
                {type === 'privacy' ? 'Privacy Policy & Data Rights' : 'Terms of Service & Travel Disclaimers'}
              </h3>
              <p className="text-xs text-slate-500 font-medium">Last updated: November 2026 • TravelPilot Autonomous AI</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-200/50 transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-4 text-sm text-slate-600 leading-relaxed">
          {type === 'privacy' ? (
            <>
              <section>
                <h4 className="font-bold text-slate-900 mb-1">1. User Data Collection</h4>
                <p>
                  TravelPilot collects account information (email, name) and trip parameters (destinations, dates, budgets,
                  food and travel preferences) to orchestrate tailored multi-agent travel plans.
                </p>
              </section>

              <section>
                <h4 className="font-bold text-slate-900 mb-1">2. AI Observability & Tracing</h4>
                <p>
                  Execution traces, latency telemetry, and model queries are monitored securely via LangSmith to guarantee
                  guardrail enforcement and continuous safety compliance. No personal financial credentials or credit card
                  numbers are ever collected.
                </p>
              </section>

              <section>
                <h4 className="font-bold text-slate-900 mb-1">3. Account Deletion & Data Export</h4>
                <p>
                  You retain full ownership of your travel data. You can export your itineraries in JSON format or request
                  permanent deletion of your account and associated trip records at any time.
                </p>
              </section>
            </>
          ) : (
            <>
              {/* Dynamic Real-time Disclaimers */}
              <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold">Real-World Information Notice:</span>
                  <p className="mt-1 leading-normal">
                    Flight schedules, hotel tariffs, weather conditions, museum admission fees, and opening hours are
                    aggregated from real-time web radar sources and can change without notice. Always verify local timings
                    and advisories prior to travel.
                  </p>
                </div>
              </div>

              <section>
                <h4 className="font-bold text-slate-900 mb-1">1. Non-Transactional Advisory Service</h4>
                <p>
                  TravelPilot v1 is an autonomous AI travel planning and intelligence engine. We do not directly sell tickets,
                  book rooms, or process payment transactions. All bookings are facilitated via direct verified external links
                  to official carriers and booking providers.
                </p>
              </section>

              <section>
                <h4 className="font-bold text-slate-900 mb-1">2. Autonomous Guardrails & Liability</h4>
                <p>
                  While our multi-agent safety shield continuously audits routes against weather disruptions, transit buffers,
                  and international advisories, travelers remain responsible for personal safety and travel documentation.
                </p>
              </section>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
          <span className="text-xs text-slate-400 font-medium">TravelPilot Enterprise • MIT ADT University</span>
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs transition-all shadow-sm"
          >
            Understood & Agree
          </button>
        </div>
      </div>
    </div>
  );
};
