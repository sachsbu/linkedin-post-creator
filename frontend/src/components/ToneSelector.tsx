import React from 'react';
import { ToneOption } from '../types';
import { Briefcase, Rocket, Code, TrendingUp } from 'lucide-react';

interface ToneSelectorProps {
  selectedTone: ToneOption;
  onSelectTone: (tone: ToneOption) => void;
}

const TONES: { id: ToneOption; label: string; icon: React.FC<{ className?: string }>; desc: string }[] = [
  { id: 'professional', label: 'Professional', icon: Briefcase, desc: 'Authoritative & polished' },
  { id: 'founder', label: 'Founder', icon: Rocket, desc: 'Visionary & strategic' },
  { id: 'developer', label: 'Developer', icon: Code, desc: 'Technical & pragmatic' },
  { id: 'investor', label: 'Investor', icon: TrendingUp, desc: 'Market & growth focused' },
];

export const ToneSelector: React.FC<ToneSelectorProps> = ({ selectedTone, onSelectTone }) => {
  return (
    <div className="flex flex-col space-y-2">
      <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
        Writing Tone & Perspective
      </label>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {TONES.map((t) => {
          const Icon = t.icon;
          const active = selectedTone === t.id;
          return (
            <button
              key={t.id}
              onClick={() => onSelectTone(t.id)}
              className={`flex items-center space-x-2 px-3 py-2 rounded-xl text-xs font-medium border transition-all text-left ${
                active
                  ? 'bg-sky-500/15 border-sky-500 text-sky-300 shadow-sm shadow-sky-500/10'
                  : 'bg-slate-800/40 border-slate-700/60 text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <Icon className={`w-4 h-4 ${active ? 'text-sky-400' : 'text-slate-400'}`} />
              <div>
                <div className="font-semibold">{t.label}</div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
