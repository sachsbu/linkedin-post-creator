import React from 'react';
import { ProviderOption } from '../types';
import { Bot, Cpu, Sparkles, Sliders } from 'lucide-react';

interface ProviderSelectorProps {
  selectedProvider: ProviderOption;
  onSelectProvider: (provider: ProviderOption) => void;
}

const PROVIDERS: { id: ProviderOption; label: string; icon: React.FC<{ className?: string }>; desc: string }[] = [
  { id: 'default', label: 'Default (.env)', icon: Sliders, desc: 'Use .env setting' },
  { id: 'gemini', label: 'Gemini', icon: Sparkles, desc: 'Google Gemini' },
  { id: 'openai', label: 'OpenAI', icon: Bot, desc: 'GPT-4o Mini' },
  { id: 'ollama', label: 'Ollama', icon: Cpu, desc: 'Local Llama' },
];

export const ProviderSelector: React.FC<ProviderSelectorProps> = ({ selectedProvider, onSelectProvider }) => {
  return (
    <div className="flex flex-col space-y-2">
      <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
        AI Provider Engine
      </label>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {PROVIDERS.map((p) => {
          const Icon = p.icon;
          const active = selectedProvider === p.id;
          return (
            <button
              key={p.id}
              onClick={() => onSelectProvider(p.id)}
              className={`flex items-center space-x-2 px-3 py-2 rounded-xl text-xs font-medium border transition-all text-left ${
                active
                  ? 'bg-purple-500/15 border-purple-500 text-purple-300 shadow-sm shadow-purple-500/10'
                  : 'bg-slate-800/40 border-slate-700/60 text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <Icon className={`w-4 h-4 ${active ? 'text-purple-400' : 'text-slate-400'}`} />
              <div>
                <div className="font-semibold">{p.label}</div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
