import { useState } from 'react';
import FindingCard from './FindingCard';

function ReportView({ scanData, onNewScan }) {
  const [filterSeverity, setFilterSeverity] = useState('all');

  const summary = scanData.summary || {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    info: 0,
  };

  const totalFindings = Object.values(summary).reduce((a, b) => a + b, 0);
  const criticalCount = summary.critical + summary.high;

  const filteredFindings = filterSeverity === 'all'
    ? scanData.findings
    : scanData.findings.filter(f => f.severity === filterSeverity);

  const downloadReport = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/scan/${scanData.scan_id}/report`);
      const data = await response.json();
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `vulnscan-report-${scanData.scan_id}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download report:', error);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-2xl shadow-2xl shadow-cyan-500/50 mb-4">
          <svg className="w-10 h-10 text-slate-950" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-4xl font-bold text-slate-100">Scan Complete</h2>
        <p className="text-slate-400 font-mono text-sm">{scanData.target_url}</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {[
          { label: 'Critical', count: summary.critical, color: 'red', gradient: 'from-red-600 to-red-700' },
          { label: 'High', count: summary.high, color: 'orange', gradient: 'from-orange-600 to-orange-700' },
          { label: 'Medium', count: summary.medium, color: 'yellow', gradient: 'from-yellow-600 to-yellow-700' },
          { label: 'Low', count: summary.low, color: 'blue', gradient: 'from-blue-600 to-blue-700' },
          { label: 'Info', count: summary.info, color: 'slate', gradient: 'from-slate-600 to-slate-700' },
        ].map((item) => (
          <button
            key={item.label}
            onClick={() => setFilterSeverity(filterSeverity === item.label.toLowerCase() ? 'all' : item.label.toLowerCase())}
            className={`bg-slate-900/50 border ${
              filterSeverity === item.label.toLowerCase() 
                ? `border-${item.color}-500/50 ring-2 ring-${item.color}-500/20` 
                : 'border-slate-800/50'
            } rounded-xl p-4 hover:bg-slate-900/70 transition-all cursor-pointer`}
          >
            <div className={`text-3xl font-bold bg-gradient-to-br ${item.gradient} bg-clip-text text-transparent mb-1`}>
              {item.count}
            </div>
            <div className="text-xs font-mono text-slate-400 uppercase tracking-wider">{item.label}</div>
          </button>
        ))}
      </div>

      {/* Overall Status */}
      <div className={`${
        criticalCount > 0 
          ? 'bg-red-500/10 border-red-500/50' 
          : totalFindings > 0
          ? 'bg-yellow-500/10 border-yellow-500/50'
          : 'bg-green-500/10 border-green-500/50'
      } border rounded-xl p-6`}>
        <div className="flex items-center gap-4">
          <div className="text-4xl">
            {criticalCount > 0 ? '⚠️' : totalFindings > 0 ? '⚡' : '✅'}
          </div>
          <div>
            <h3 className={`text-xl font-bold mb-1 ${
              criticalCount > 0 
                ? 'text-red-400' 
                : totalFindings > 0
                ? 'text-yellow-400'
                : 'text-green-400'
            }`}>
              {criticalCount > 0 
                ? 'Critical Issues Found' 
                : totalFindings > 0
                ? 'Vulnerabilities Detected'
                : 'No Critical Issues'}
            </h3>
            <p className="text-slate-400 text-sm">
              {totalFindings === 0 
                ? 'Basic security checks passed successfully'
                : `Found ${totalFindings} issue${totalFindings !== 1 ? 's' : ''} across ${filteredFindings.length > 0 ? 'multiple' : 'various'} categories`}
            </p>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-4">
        <button
          onClick={downloadReport}
          className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 px-6 py-3 rounded-lg transition-colors font-medium"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Download JSON Report
        </button>
        
        <button
          onClick={onNewScan}
          className="flex items-center gap-2 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-slate-950 px-6 py-3 rounded-lg transition-all font-bold shadow-lg shadow-cyan-500/30"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Scan
        </button>
      </div>

      {/* Filter Info */}
      {filterSeverity !== 'all' && (
        <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-lg p-4 flex items-center justify-between">
          <p className="text-cyan-400 text-sm font-mono">
            Showing {filteredFindings.length} {filterSeverity} severity issue{filteredFindings.length !== 1 ? 's' : ''}
          </p>
          <button
            onClick={() => setFilterSeverity('all')}
            className="text-cyan-400 hover:text-cyan-300 text-sm font-mono underline"
          >
            Clear filter
          </button>
        </div>
      )}

      {/* Findings List */}
      <div className="space-y-4">
        <div className="flex items-center gap-3 mb-4">
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent"></div>
          <span className="text-sm font-mono text-cyan-400/60">
            {filteredFindings.length} FINDING{filteredFindings.length !== 1 ? 'S' : ''}
          </span>
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent"></div>
        </div>

        {filteredFindings.length > 0 ? (
          filteredFindings.map((finding, idx) => (
            <FindingCard key={idx} finding={finding} />
          ))
        ) : (
          <div className="text-center py-12 bg-slate-900/30 border border-slate-800/50 rounded-xl">
            <svg className="w-16 h-16 text-slate-700 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-slate-500">No findings for this severity level</p>
          </div>
        )}
      </div>

      {/* Scan Metadata */}
      <div className="bg-slate-900/30 border border-slate-800/50 rounded-xl p-6 space-y-3">
        <h3 className="text-slate-300 font-semibold mb-4 flex items-center gap-2">
          <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Scan Information
        </h3>
        <div className="grid md:grid-cols-2 gap-3 text-sm">
          <div>
            <span className="text-slate-500 font-mono">Scan ID:</span>
            <p className="text-slate-300 font-mono break-all">{scanData.scan_id}</p>
          </div>
          <div>
            <span className="text-slate-500 font-mono">Target:</span>
            <p className="text-slate-300 font-mono break-all">{scanData.target_url}</p>
          </div>
          <div>
            <span className="text-slate-500 font-mono">Started:</span>
            <p className="text-slate-300">{new Date(scanData.started_at).toLocaleString()}</p>
          </div>
          <div>
            <span className="text-slate-500 font-mono">Completed:</span>
            <p className="text-slate-300">{new Date(scanData.completed_at).toLocaleString()}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReportView;
