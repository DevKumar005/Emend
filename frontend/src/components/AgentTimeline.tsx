import React, { useEffect, useRef, useState } from 'react';
import { AgentEvent } from '../types';
import { Terminal, ChevronDown, ChevronRight, ArrowDown, Copy, Check } from 'lucide-react';

interface AgentTimelineProps {
  events: AgentEvent[];
}

export const AgentTimeline: React.FC<AgentTimelineProps> = ({ events }) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [expandedIndices, setExpandedIndices] = useState<Record<number, boolean>>({});
  const [filterType, setFilterType] = useState<string>('all');
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events, autoScroll]);

  const toggleExpand = (idx: number) => {
    setExpandedIndices(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  const handleCopyPayload = (idx: number, payload: any) => {
    navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 1500);
  };

  const formatTimestamp = (ts: string | number | undefined): string => {
    if (ts === undefined || ts === null) return '';
    if (typeof ts === 'number') {
      const d = new Date(ts > 1e11 ? ts : ts * 1000);
      return d.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }
    if (typeof ts === 'string') {
      if (ts.includes('T')) {
        return ts.split('T')[1].replace('Z', '').split('.')[0];
      }
      const num = Number(ts);
      if (!isNaN(num)) {
        return formatTimestamp(num);
      }
      return ts;
    }
    return String(ts);
  };

  const getEventBadge = (type: string) => {
    switch (type) {
      case 'stage':
        return 'text-blue-700 bg-blue-50 border-blue-200';
      case 'model_message':
        return 'text-purple-700 bg-purple-50 border-purple-200';
      case 'tool_call':
        return 'text-amber-700 bg-amber-50 border-amber-200';
      case 'test_result':
        return 'text-emerald-700 bg-emerald-50 border-emerald-200';
      case 'error':
        return 'text-rose-700 bg-rose-50 border-rose-200';
      case 'verdict':
      default:
        return 'text-slate-700 bg-slate-100 border-slate-200';
    }
  };

  const filteredEvents = events.filter(e => {
    if (filterType === 'all') return true;
    return e.type === filterType;
  });

  return (
    <div className="bg-white rounded-lg border border-slate-200 flex flex-col h-[520px]">
      <div className="flex items-center justify-between p-3.5 border-b border-slate-200 bg-slate-50/70 text-xs rounded-t-lg">
        <div className="flex items-center space-x-2">
          <Terminal className="w-3.5 h-3.5 text-blue-600" />
          <span className="font-mono font-bold uppercase text-slate-800">
            Execution Stream
          </span>
          <span className="font-mono text-[10px] text-slate-500 px-1.5 py-0.5 rounded bg-white border border-slate-200">
            {events.length}
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-white border border-slate-200 text-slate-700 rounded px-2 py-1 text-xs font-mono focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Events</option>
            <option value="stage">Stages</option>
            <option value="test_result">Tests</option>
            <option value="tool_call">Patches</option>
            <option value="verdict">Verdicts</option>
          </select>

          <button
            onClick={() => setAutoScroll(!autoScroll)}
            className={`flex items-center space-x-1 px-2.5 py-1 rounded font-mono text-[11px] transition-colors ${
              autoScroll
                ? 'bg-slate-900 text-white font-medium'
                : 'text-slate-600 hover:text-slate-900 bg-slate-100'
            }`}
          >
            <ArrowDown className="w-3 h-3" />
            <span>Scroll {autoScroll ? 'ON' : 'OFF'}</span>
          </button>
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-1.5 font-mono text-xs">
        {filteredEvents.length === 0 ? (
          <div className="h-full flex items-center justify-center text-slate-400 text-xs">
            Awaiting streaming events...
          </div>
        ) : (
          filteredEvents.map((evt, idx) => {
            const isExpanded = !!expandedIndices[idx];
            const hasPayload = Object.keys(evt.payload || {}).length > 0;
            const timeStr = formatTimestamp(evt.ts);

            return (
              <div
                key={idx}
                className="p-2.5 rounded bg-slate-50 border border-slate-200 hover:border-slate-300 transition-colors"
              >
                <div className="flex items-start justify-between gap-1.5 sm:gap-2">
                  <div className="flex items-start space-x-1.5 sm:space-x-2 min-w-0 flex-1">
                    <span className="text-slate-400 text-[10px] sm:text-[11px] flex-shrink-0 mt-0.5">
                      {timeStr || '00:00:00'}
                    </span>
                    <span className={`text-[8px] sm:text-[9px] uppercase font-bold px-1.5 py-0.5 rounded border flex-shrink-0 ${getEventBadge(evt.type)}`}>
                      {evt.type}
                    </span>
                    <span className="text-slate-800 break-words font-medium leading-snug text-[11px] sm:text-xs">
                      {evt.title}
                    </span>
                  </div>

                  {hasPayload && (
                    <button
                      onClick={() => toggleExpand(idx)}
                      className="text-slate-500 hover:text-slate-800 text-[10px] flex items-center space-x-0.5 px-1.5 py-0.5 rounded bg-white border border-slate-200 flex-shrink-0"
                    >
                      <span>{isExpanded ? 'Less' : 'Data'}</span>
                      {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                    </button>
                  )}
                </div>

                {isExpanded && hasPayload && (
                  <div className="mt-2 pt-2 border-t border-slate-200">
                    <div className="flex items-center justify-between mb-1 text-[10px] text-slate-500">
                      <span>Payload Details:</span>
                      <button
                        onClick={() => handleCopyPayload(idx, evt.payload)}
                        className="flex items-center space-x-1 text-slate-600 hover:text-slate-900"
                      >
                        {copiedIdx === idx ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                        <span>{copiedIdx === idx ? 'Copied' : 'Copy'}</span>
                      </button>
                    </div>
                    <pre className="p-2 rounded bg-slate-900 text-slate-100 text-[11px] overflow-x-auto whitespace-pre-wrap">
                      {JSON.stringify(evt.payload, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
