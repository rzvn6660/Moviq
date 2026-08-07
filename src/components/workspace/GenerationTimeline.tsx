import React, { useState, useEffect } from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  Loader2, 
  ChevronDown, 
  ChevronRight, 
  Download, 
  FileText, 
  Activity,
  Cpu,
  Sparkles,
  ShieldCheck,
  Video,
  Database
} from 'lucide-react';
import { resolveMediaUrl } from '../../utils/formatters';

export interface GenerationEvent {
  id: string;
  generationId: string;
  step: string;
  status: string;
  startedAt: string;
  completedAt?: string;
  durationMs?: number;
  details?: Record<string, any>;
}

interface GenerationTimelineProps {
  generationId: string;
}

export const GenerationTimeline: React.FC<GenerationTimelineProps> = ({ generationId }) => {
  const [events, setEvents] = useState<GenerationEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedEvents, setExpandedEvents] = useState<Record<string, boolean>>({});

  useEffect(() => {
    let isMounted = true;

    const fetchEvents = async () => {
      try {
        setLoading(true);
        const url = resolveMediaUrl(`/api/v1/generations/${generationId}/events`);
        const res = await fetch(url);
        if (!res.ok) {
          throw new Error(`HTTP error ${res.status}`);
        }
        const data = await res.json();
        if (isMounted) {
          setEvents(data);
          setError(null);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to load timeline events');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchEvents();
    return () => {
      isMounted = false;
    };
  }, [generationId]);

  const toggleExpand = (eventId: string) => {
    setExpandedEvents(prev => ({ ...prev, [eventId]: !prev[eventId] }));
  };

  const getStepLabel = (step: string) => {
    switch (step) {
      case 'PROMPT_RECEIVED':
        return 'Prompt Submitted';
      case 'DIRECTOR_STARTED':
      case 'DIRECTOR_COMPLETED':
        return 'AI Director Enhancement';
      case 'PROVIDER_SELECTED':
        return 'Provider Selection';
      case 'GENERATION_SUBMITTED':
        return 'Job Submitted';
      case 'QUEUE_STARTED':
        return 'In Provider Queue';
      case 'GENERATION_STARTED':
      case 'GENERATION_PROGRESS':
        return 'Generating Video Diffusion Frames';
      case 'VIDEO_DOWNLOADING':
      case 'VIDEO_DOWNLOADED':
        return 'Downloading Result Payload';
      case 'VIDEO_VALIDATING':
      case 'VIDEO_VALIDATED':
        return 'Video Stream Validation';
      case 'THUMBNAIL_GENERATED':
        return 'Thumbnail Frame Extraction';
      case 'DATABASE_UPDATED':
        return 'State Record Persisted';
      case 'COMPLETED':
        return 'Generation Complete';
      case 'FAILED':
        return 'Generation Failed';
      case 'CANCELLED':
        return 'Generation Cancelled';
      default:
        return step.replace(/_/g, ' ');
    }
  };

  const getStepIcon = (step: string, status: string) => {
    if (status === 'FAILED') return <AlertTriangle className="w-4 h-4 text-rose-400" />;
    if (status === 'RUNNING') return <Loader2 className="w-4 h-4 text-amber-400 animate-spin" />;
    
    switch (step) {
      case 'PROMPT_RECEIVED':
        return <Activity className="w-4 h-4 text-sky-400" />;
      case 'DIRECTOR_STARTED':
      case 'DIRECTOR_COMPLETED':
        return <Sparkles className="w-4 h-4 text-purple-400" />;
      case 'PROVIDER_SELECTED':
        return <Cpu className="w-4 h-4 text-indigo-400" />;
      case 'VIDEO_VALIDATED':
        return <ShieldCheck className="w-4 h-4 text-emerald-400" />;
      case 'VIDEO_DOWNLOADED':
        return <Video className="w-4 h-4 text-amber-400" />;
      case 'DATABASE_UPDATED':
        return <Database className="w-4 h-4 text-slate-400" />;
      default:
        return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
    }
  };

  const formatTimestamp = (isoStr: string) => {
    if (!isoStr) return '--:--:--';
    try {
      const d = new Date(isoStr);
      return d.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) +
        '.' + d.getMilliseconds().toString().padStart(3, '0');
    } catch {
      return isoStr;
    }
  };

  const formatDuration = (ms?: number) => {
    if (ms === undefined || ms === null) return '';
    if (ms < 1000) return `${ms} ms`;
    return `${(ms / 1000).toFixed(2)} s`;
  };

  const handleExportJSON = () => {
    const jsonStr = JSON.stringify(events, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `moviq-timeline-${generationId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportMarkdown = () => {
    let md = `# MOVIQ Generation Execution Timeline\n\n`;
    md += `**Generation ID:** \`${generationId}\`\n`;
    md += `**Event Count:** ${events.length}\n\n`;
    md += `| Timestamp | Step | Status | Duration | Details |\n`;
    md += `| :--- | :--- | :--- | :--- | :--- |\n`;

    events.forEach(e => {
      const time = formatTimestamp(e.startedAt);
      const label = getStepLabel(e.step);
      const dur = formatDuration(e.durationMs);
      const detailsStr = e.details ? JSON.stringify(e.details) : '-';
      md += `| ${time} | ${label} | ${e.status} | ${dur} | \`${detailsStr}\` |\n`;
    });

    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `moviq-timeline-${generationId}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="p-4 rounded-xl bg-[#0c1324] border border-[#23293c] flex items-center justify-center gap-2 text-xs text-slate-400">
        <Loader2 className="w-4 h-4 text-amber-400 animate-spin" />
        <span>Loading generation timeline events...</span>
      </div>
    );
  }

  if (error || events.length === 0) {
    return (
      <div className="p-4 rounded-xl bg-[#0c1324] border border-[#23293c] text-xs text-slate-400">
        <span className="text-amber-400 font-semibold block mb-1">Timeline Observability</span>
        <span>{error || 'No timeline events recorded yet.'}</span>
      </div>
    );
  }

  const totalDurationMs = events.reduce((acc, ev) => acc + (ev.durationMs || 0), 0);

  return (
    <div className="p-4 rounded-xl bg-[#0c1324] border border-[#23293c] space-y-4 text-xs">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#23293c] pb-2.5">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-amber-400" />
          <span className="font-semibold text-slate-100 uppercase tracking-wider text-xs">Generation Execution Timeline</span>
          <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 font-mono">
            {events.length} Events ({formatDuration(totalDurationMs)} Total)
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleExportJSON}
            className="px-2 py-1 rounded bg-[#151b2d] hover:bg-[#1e2638] text-slate-300 border border-[#23293c] text-[10px] font-medium flex items-center gap-1.5 transition-colors"
            title="Export Timeline as JSON"
          >
            <Download className="w-3 h-3 text-amber-400" />
            <span>JSON</span>
          </button>
          <button
            onClick={handleExportMarkdown}
            className="px-2 py-1 rounded bg-[#151b2d] hover:bg-[#1e2638] text-slate-300 border border-[#23293c] text-[10px] font-medium flex items-center gap-1.5 transition-colors"
            title="Export Timeline as Markdown"
          >
            <FileText className="w-3 h-3 text-amber-400" />
            <span>Markdown</span>
          </button>
        </div>
      </div>

      {/* Vertical Timeline List */}
      <div className="relative pl-5 space-y-3 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#23293c]">
        {events.map((evt) => {
          const isExpanded = !!expandedEvents[evt.id];
          const hasDetails = evt.details && Object.keys(evt.details).length > 0;
          const isFailed = evt.status === 'FAILED';

          return (
            <div key={evt.id} className="relative group">
              {/* Point Indicator */}
              <div className="absolute -left-5 top-0.5 p-0.5 rounded-full bg-[#0c1324]">
                {getStepIcon(evt.step, evt.status)}
              </div>

              {/* Step Card */}
              <div className={`p-2.5 rounded-lg border transition-all ${
                isFailed 
                  ? 'bg-rose-500/10 border-rose-500/30' 
                  : 'bg-[#151b2d] border-[#23293c] hover:border-slate-700'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`font-semibold text-xs ${isFailed ? 'text-rose-300' : 'text-slate-200'}`}>
                      {getStepLabel(evt.step)}
                    </span>
                    {evt.status === 'FAILED' && (
                      <span className="text-[9px] px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-300 font-mono uppercase font-bold">
                        Failed
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-[10px] text-slate-400 font-mono">
                      {formatTimestamp(evt.startedAt)}
                    </span>
                    {evt.durationMs !== undefined && evt.durationMs > 0 && (
                      <span className="text-[10px] text-amber-400 font-mono bg-amber-500/10 px-1.5 py-0.5 rounded">
                        {formatDuration(evt.durationMs)}
                      </span>
                    )}
                    {hasDetails && (
                      <button
                        onClick={() => toggleExpand(evt.id)}
                        className="text-slate-400 hover:text-slate-200 p-0.5 transition-colors"
                      >
                        {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                      </button>
                    )}
                  </div>
                </div>

                {/* Expandable Technical Details */}
                {hasDetails && isExpanded && (
                  <div className="mt-2.5 pt-2 border-t border-[#23293c] text-[11px] font-mono text-slate-300 bg-[#0c1324] p-2 rounded border border-[#1e2638] overflow-x-auto">
                    <pre className="text-[10px] leading-relaxed text-amber-300/90 whitespace-pre-wrap">
                      {JSON.stringify(evt.details, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
