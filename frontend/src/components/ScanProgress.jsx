import { useState, useEffect } from 'react';

function ScanProgress({ scanId, onComplete, onNewScan }) {
  const [scanData, setScanData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let interval;

    const fetchScanStatus = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/scan/${scanId}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch scan status');
        }

        const data = await response.json();
        setScanData(data);

        if (data.status === 'completed') {
          clearInterval(interval);
          setTimeout(() => onComplete(data), 1000);
        } else if (data.status === 'failed') {
          clearInterval(interval);
          setError(data.error || 'Scan failed');
        }
      } catch (err) {
        setError(err.message);
        clearInterval(interval);
      }
    };

    // Initial fetch
    fetchScanStatus();

    // Poll every second
    interval = setInterval(fetchScanStatus, 1000);

    return () => clearInterval(interval);
  }, [scanId, onComplete]);

  if (error) {
    return (
      <div className="max-w-2xl mx-auto animate-fadeIn">
        <div className="bg-red-500/10 border border-red-500/50 rounded-2xl p-8 text-center">
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-red-400 mb-2">Scan Failed</h2>
          <p className="text-red-400/70 mb-6">{error}</p>
          <button
            onClick={onNewScan}
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 px-6 py-3 rounded-lg transition-colors"
          >
            Start New Scan
          </button>
        </div>
      </div>
    );
  }

  if (!scanData) {
    return (
      <div className="max-w-2xl mx-auto text-center">
        <div className="animate-pulse">
          <div className="w-16 h-16 bg-cyan-500/20 rounded-full mx-auto mb-4"></div>
          <p className="text-slate-400">Loading scan status...</p>
        </div>
      </div>
    );
  }

  const progressPercentage = scanData.progress || 0;

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-slate-100 mb-2">Scanning in Progress</h2>
        <p className="text-slate-400 font-mono text-sm">{scanData.target_url}</p>
      </div>

      {/* Main Progress Card */}
      <div className="bg-slate-900/50 backdrop-blur-sm border border-cyan-500/20 rounded-2xl p-8 shadow-2xl shadow-cyan-500/10">
        {/* Status Indicator */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="relative">
            <div className="w-3 h-3 bg-cyan-400 rounded-full animate-ping absolute"></div>
            <div className="w-3 h-3 bg-cyan-400 rounded-full"></div>
          </div>
          <span className="text-cyan-400 font-mono text-sm uppercase tracking-wider">
            {scanData.status === 'running' ? 'Active Scan' : 'Queued'}
          </span>
        </div>

        {/* Current Check */}
        <div className="text-center mb-8">
          <p className="text-slate-500 text-sm mb-2 font-mono">CURRENT CHECK</p>
          <p className="text-xl font-semibold text-slate-200">
            {scanData.current_check || 'Initializing...'}
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-3">
            <span className="text-sm font-mono text-slate-400">Progress</span>
            <span className="text-sm font-mono text-cyan-400 font-bold">{progressPercentage}%</span>
          </div>
          <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-500 ease-out relative overflow-hidden"
              style={{ width: `${progressPercentage}%` }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
            </div>
          </div>
        </div>

        {/* Scan Stages */}
        <div className="space-y-3">
          {[
            { name: 'Security Headers', progress: 10 },
            { name: 'SSL/TLS Configuration', progress: 30 },
            { name: 'XSS Detection', progress: 50 },
            { name: 'SQL Injection Detection', progress: 70 },
            { name: 'Information Disclosure', progress: 90 },
          ].map((stage) => (
            <div key={stage.name} className="flex items-center gap-3">
              <div className="flex-shrink-0">
                {progressPercentage >= stage.progress ? (
                  <svg className="w-5 h-5 text-cyan-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                ) : progressPercentage >= stage.progress - 20 ? (
                  <div className="w-5 h-5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <div className="w-5 h-5 border-2 border-slate-700 rounded-full"></div>
                )}
              </div>
              <span className={`text-sm font-mono ${
                progressPercentage >= stage.progress 
                  ? 'text-slate-300' 
                  : progressPercentage >= stage.progress - 20
                  ? 'text-cyan-400'
                  : 'text-slate-600'
              }`}>
                {stage.name}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Stats Preview */}
      {scanData.findings && scanData.findings.length > 0 && (
        <div className="bg-slate-900/30 border border-slate-800/50 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="text-slate-300 font-semibold">Findings Detected</h3>
          </div>
          <p className="text-slate-400 text-sm">
            {scanData.findings.length} issue{scanData.findings.length !== 1 ? 's' : ''} found so far...
          </p>
        </div>
      )}

      <style>{`
        @keyframes shimmer {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }
        
        .animate-shimmer {
          animation: shimmer 2s infinite;
        }
      `}</style>
    </div>
  );
}

export default ScanProgress;
