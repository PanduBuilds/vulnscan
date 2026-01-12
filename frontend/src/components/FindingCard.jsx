import { useState } from 'react';

const SEVERITY_CONFIG = {
  critical: {
    color: 'from-red-600 to-red-700',
    bg: 'bg-red-500/10',
    border: 'border-red-500/50',
    text: 'text-red-400',
    icon: '🔴',
  },
  high: {
    color: 'from-orange-600 to-orange-700',
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/50',
    text: 'text-orange-400',
    icon: '🟠',
  },
  medium: {
    color: 'from-yellow-600 to-yellow-700',
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/50',
    text: 'text-yellow-400',
    icon: '🟡',
  },
  low: {
    color: 'from-blue-600 to-blue-700',
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/50',
    text: 'text-blue-400',
    icon: '🔵',
  },
  info: {
    color: 'from-slate-600 to-slate-700',
    bg: 'bg-slate-500/10',
    border: 'border-slate-500/50',
    text: 'text-slate-400',
    icon: 'ℹ️',
  },
};

function FindingCard({ finding }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const config = SEVERITY_CONFIG[finding.severity] || SEVERITY_CONFIG.info;

  return (
    <div className={`${config.bg} border ${config.border} rounded-xl overflow-hidden transition-all hover:shadow-lg`}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-5 text-left flex items-start gap-4 hover:bg-white/5 transition-colors"
      >
        {/* Severity Badge */}
        <div className={`flex-shrink-0 w-10 h-10 bg-gradient-to-br ${config.color} rounded-lg flex items-center justify-center text-lg shadow-lg`}>
          {config.icon}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-4 mb-2">
            <h3 className="text-slate-200 font-semibold leading-tight pr-4">
              {finding.title}
            </h3>
            <span className={`flex-shrink-0 px-3 py-1 rounded-full text-xs font-mono uppercase tracking-wider ${config.text} ${config.bg} border ${config.border}`}>
              {finding.severity}
            </span>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-2 mb-2">
            {finding.cwe_id && (
              <span className="px-2 py-1 bg-slate-800/50 border border-slate-700 rounded text-xs text-slate-400 font-mono">
                {finding.cwe_id}
              </span>
            )}
            {finding.owasp_category && (
              <span className="px-2 py-1 bg-slate-800/50 border border-slate-700 rounded text-xs text-slate-400 font-mono">
                {finding.owasp_category}
              </span>
            )}
          </div>

          {/* Expand indicator */}
          <div className="flex items-center gap-2 text-sm text-slate-500 font-mono">
            <span>{isExpanded ? 'Hide details' : 'Show details'}</span>
            <svg
              className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </button>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="border-t border-slate-800/50 p-5 space-y-4 bg-slate-950/30 animate-slideDown">
          {/* Description */}
          <div>
            <h4 className="text-sm font-mono text-cyan-400 mb-2 uppercase tracking-wider">Description</h4>
            <p className="text-slate-300 text-sm leading-relaxed">{finding.description}</p>
          </div>

          {/* Evidence */}
          <div>
            <h4 className="text-sm font-mono text-cyan-400 mb-2 uppercase tracking-wider">Evidence</h4>
            <div className="bg-slate-950/50 border border-slate-800 rounded-lg p-3">
              <code className="text-slate-300 text-sm font-mono break-all">{finding.evidence}</code>
            </div>
          </div>

          {/* Remediation */}
          <div>
            <h4 className="text-sm font-mono text-cyan-400 mb-2 uppercase tracking-wider">Remediation</h4>
            <p className="text-slate-300 text-sm leading-relaxed">{finding.remediation}</p>
          </div>
        </div>
      )}

      <style>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            max-height: 0;
          }
          to {
            opacity: 1;
            max-height: 1000px;
          }
        }
        
        .animate-slideDown {
          animation: slideDown 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}

export default FindingCard;
