import React, { useEffect, useState, useRef } from 'react';
import { Bot, Send, Sparkles, ShieldAlert, CornerDownLeft, RefreshCw, User, Cpu } from 'lucide-react';
import { api } from '../services/api';
import { Incident, CopilotMessage, CopilotSuggestion } from '../types';
import { useToast } from '../components/Toast';

interface CopilotPageProps {
  onNavigate: (path: string) => void;
}

export const CopilotPage: React.FC<CopilotPageProps> = ({ onNavigate }) => {
  const { showToast } = useToast();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string>('');
  const [suggestions, setSuggestions] = useState<CopilotSuggestion[]>([]);
  const [messages, setMessages] = useState<CopilotMessage[]>([
    {
      id: 'welcome',
      sender: 'copilot',
      text: "Hello, Analyst. I am SentinelAI-X Copilot, your autonomous cybersecurity investigation assistant.\n\nSelect an active incident from the selector above to ground our conversation in live telemetry, or ask any question regarding attack patterns, MITRE techniques, risk scoring formulas, or response playbooks.",
      timestamp: new Date().toLocaleTimeString(),
      suggestedFollowups: [
        'How does SentinelAI-X calculate risk scores?',
        'Explain MITRE T1110 brute force defense',
        'Show containment command templates',
      ],
    },
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [incList, sugList] = await Promise.all([
          api.getIncidents({ page_size: 50 }),
          api.getCopilotSuggestions(),
        ]);
        setIncidents(incList);
        setSuggestions(sugList);
      } catch (err) {
        console.error('Failed to load copilot init data:', err);
      }
    };
    loadData();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSendMessage = async (textToSend?: string) => {
    const query = (textToSend || inputQuery).trim();
    if (!query || isTyping) return;

    const userMsg: CopilotMessage = {
      id: Math.random().toString(),
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputQuery('');
    setIsTyping(true);

    try {
      const history = messages.slice(-4).map((m) => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.text,
      }));

      const res = await api.copilotChat(
        query,
        selectedIncidentId || undefined,
        history
      );

      const copilotMsg: CopilotMessage = {
        id: Math.random().toString(),
        sender: 'copilot',
        text: res.reply,
        timestamp: new Date().toLocaleTimeString(),
        suggestedFollowups: res.suggested_followups,
        referencedEvidence: res.referenced_evidence,
        mitreReferences: res.mitre_references,
        copilotMode: res.copilot_mode,
      };

      setMessages((prev) => [...prev, copilotMsg]);
    } catch (err: any) {
      showToast('error', 'Copilot Query Failed', err.message);
      setMessages((prev) => [
        ...prev,
        {
          id: Math.random().toString(),
          sender: 'copilot',
          text: `⚠️ I encountered an error connecting to the intelligence engine: ${err.message}. Please verify backend status.`,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSuggestionClick = (prompt: string) => {
    handleSendMessage(prompt);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      {/* Top Header & Incident Context Selector */}
      <div className="cream-card p-6 border-l-4 border-l-caramel flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-caramel text-[13px] font-bold uppercase tracking-wider mb-1">
            <Sparkles className="w-4 h-4" />
            <span>Autonomous SOC Intelligence</span>
          </div>
          <h1 className="text-[26px] font-black text-espresso-900 tracking-tight">
            AI Investigation Copilot
          </h1>
          <p className="text-[14px] text-charcoal-muted mt-0.5">
            Context-grounded assistant for rapid threat analysis, MITRE evaluation, and containment playbook generation.
          </p>
        </div>

        {/* Incident Context Selector */}
        <div className="shrink-0">
          <label className="block text-[12px] font-extrabold text-charcoal-muted uppercase tracking-wider mb-1">
            Active Incident Grounding Context
          </label>
          <select
            value={selectedIncidentId}
            onChange={(e) => setSelectedIncidentId(e.target.value)}
            className="w-full md:w-72 px-3.5 py-2 rounded-xl border border-cream-300 bg-cream-100 text-espresso-900 font-bold text-[13.5px] focus:outline-none focus:border-caramel"
          >
            <option value="">🌐 General SOC Knowledge (No specific incident)</option>
            {incidents.map((inc) => (
              <option key={inc.id} value={inc.incident_id}>
                {inc.incident_id} — {inc.title.slice(0, 32)}...
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Recommended Prompt Chips */}
      {suggestions.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[12.5px] font-bold text-charcoal-muted uppercase tracking-wider mr-1">
            Quick Prompts:
          </span>
          {suggestions.map((sug) => (
            <button
              key={sug.id}
              onClick={() => handleSuggestionClick(sug.prompt)}
              className="px-3.5 py-1.5 rounded-full bg-white hover:bg-cream-200 border border-cream-300 text-espresso-900 text-[13.5px] font-semibold transition-all shadow-xs hover:border-caramel"
            >
              {sug.prompt}
            </button>
          ))}
        </div>
      )}

      {/* Chat Stream Window */}
      <div className="cream-card flex flex-col h-[600px] overflow-hidden shadow-card">
        {/* Messages Scroll Area */}
        <div className="flex-1 p-6 overflow-y-auto space-y-6">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start gap-3.5 ${
                msg.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.sender === 'copilot' && (
                <div className="w-9 h-9 rounded-xl bg-espresso-900 text-caramel flex items-center justify-center shrink-0 font-bold shadow-xs">
                  <Bot className="w-5 h-5" />
                </div>
              )}

              <div
                className={`max-w-2xl rounded-2xl p-5 shadow-xs leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-espresso-900 text-cream-100 font-medium text-[15px]'
                    : 'bg-cream-100 border border-cream-200 text-charcoal text-[15px]'
                }`}
              >
                <div className="whitespace-pre-wrap leading-relaxed font-sans">
                  {msg.text}
                </div>

                {/* Copilot Follow-up Suggestion Chips */}
                {msg.suggestedFollowups && msg.suggestedFollowups.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-cream-200/80">
                    <p className="text-[12px] font-bold text-charcoal-muted uppercase tracking-wider mb-2">
                      Suggested Investigation Follow-ups:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {msg.suggestedFollowups.map((f, i) => (
                        <button
                          key={i}
                          onClick={() => handleSuggestionClick(f)}
                          className="px-3 py-1 rounded-lg bg-cream-200 hover:bg-cream-300 border border-cream-300 text-espresso-900 text-[12.5px] font-bold transition-colors text-left"
                        >
                          → {f}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                <div className="mt-2 text-right">
                  <span
                    className={`text-[11px] ${
                      msg.sender === 'user' ? 'text-cream-400' : 'text-charcoal-subtle'
                    }`}
                  >
                    {msg.timestamp}
                  </span>
                </div>
              </div>

              {msg.sender === 'user' && (
                <div className="w-9 h-9 rounded-xl bg-caramel text-white flex items-center justify-center shrink-0 font-bold shadow-xs">
                  <User className="w-5 h-5" />
                </div>
              )}
            </div>
          ))}

          {isTyping && (
            <div className="flex items-start gap-3.5">
              <div className="w-9 h-9 rounded-xl bg-espresso-900 text-caramel flex items-center justify-center shrink-0 font-bold">
                <Bot className="w-5 h-5" />
              </div>
              <div className="bg-cream-100 border border-cream-200 rounded-2xl p-4 flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-caramel animate-bounce" />
                <div className="w-2 h-2 rounded-full bg-caramel animate-bounce [animation-delay:0.2s]" />
                <div className="w-2 h-2 rounded-full bg-caramel animate-bounce [animation-delay:0.4s]" />
                <span className="text-[13px] font-semibold text-charcoal-muted ml-2">
                  Gemini analyzing telemetry...
                </span>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 bg-white border-t border-cream-200">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-center gap-3"
          >
            <input
              type="text"
              placeholder={
                selectedIncidentId
                  ? `Ask Copilot about ${selectedIncidentId} (e.g. "Generate firewall block rule", "Explain evidence")...`
                  : 'Ask any cybersecurity investigation question...'
              }
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              className="flex-1 px-4 py-3 rounded-xl border border-cream-300 bg-cream-100 text-espresso-900 font-medium text-[15px] focus:outline-none focus:border-caramel"
            />
            <button
              type="submit"
              disabled={isTyping || !inputQuery.trim()}
              className="px-6 py-3 rounded-xl bg-espresso-900 hover:bg-espresso-800 text-cream-100 font-extrabold text-[15px] shadow-sm disabled:opacity-50 transition-all flex items-center gap-2 shrink-0"
            >
              <span>Ask</span>
              <Send className="w-4 h-4 text-caramel" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
