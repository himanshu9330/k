import React, { useEffect, useState } from 'react';
import { Layers, Search, ExternalLink, ShieldCheck, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { MitreTechnique } from '../types';

export const MitrePage: React.FC = () => {
  const [techniques, setTechniques] = useState<MitreTechnique[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTactic, setSelectedTactic] = useState<string>('ALL');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadMitre = async () => {
      setIsLoading(true);
      try {
        const data = await api.getMitreTechniques();
        setTechniques(data);
      } catch (err) {
        console.error('Failed to load MITRE matrix:', err);
      } finally {
        setIsLoading(false);
      }
    };
    loadMitre();
  }, []);

  const tactics = ['ALL', ...Array.from(new Set(techniques.map((t) => t.tactic)))];

  const filtered = techniques.filter((t) => {
    const matchSearch =
      t.technique_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchTactic = selectedTactic === 'ALL' || t.tactic === selectedTactic;
    return matchSearch && matchTactic;
  });

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16">
      {/* Header */}
      <div>
        <h1 className="text-[28px] md:text-[32px] font-black text-espresso-900 tracking-tight">
          MITRE ATT&CK Enterprise Framework
        </h1>
        <p className="text-[15px] text-charcoal-muted mt-1">
          Embedded adversarial tactics, techniques, and automated mitigation mappings.
        </p>
      </div>

      {/* Filter Bar */}
      <div className="cream-card p-5">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="relative sm:col-span-2">
            <Search className="w-5 h-5 absolute left-3.5 top-3 text-charcoal-muted" />
            <input
              type="text"
              placeholder="Search technique ID (T1110), name, or keyword..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-cream-300 bg-cream-100 text-espresso-900 font-medium text-[15px] focus:outline-none focus:border-caramel"
            />
          </div>

          <div>
            <select
              value={selectedTactic}
              onChange={(e) => setSelectedTactic(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-cream-300 bg-cream-100 text-espresso-900 font-bold text-[14.5px] focus:outline-none focus:border-caramel"
            >
              {tactics.map((tac) => (
                <option key={tac} value={tac}>
                  {tac === 'ALL' ? 'All Tactics' : tac}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Techniques Grid */}
      {isLoading ? (
        <div className="p-12 text-center">
          <div className="w-10 h-10 rounded-full border-4 border-espresso-800 border-t-caramel animate-spin mx-auto" />
          <p className="mt-3 font-bold text-espresso-900">Loading MITRE ATT&CK matrix...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.map((t) => (
            <div
              key={t.technique_id}
              className="cream-card p-5 flex flex-col justify-between hover:shadow-elevated transition-shadow"
            >
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded bg-espresso-900 text-cream-100 font-mono font-black text-[13px]">
                    {t.technique_id}
                  </span>
                  <span className="px-2.5 py-0.5 rounded bg-cream-200 text-copper font-bold text-[12px]">
                    {t.tactic}
                  </span>
                </div>

                <h3 className="font-extrabold text-[17px] text-espresso-900">
                  {t.name}
                </h3>

                <p className="text-[14px] text-charcoal leading-relaxed line-clamp-3">
                  {t.description}
                </p>

                {t.mitigation && (
                  <div className="pt-2 border-t border-cream-200">
                    <p className="text-[12px] font-extrabold text-charcoal-muted uppercase tracking-wider">
                      Mitigation:
                    </p>
                    <p className="text-[13px] text-espresso-800 font-medium mt-0.5">
                      {t.mitigation}
                    </p>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-cream-200 flex justify-end">
                <a
                  href={t.url || `https://attack.mitre.org/techniques/${t.technique_id}/`}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1 text-[13px] font-bold text-caramel hover:text-copper"
                >
                  <span>MITRE Reference</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
