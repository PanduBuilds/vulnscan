import { useState } from 'react';

const DEMO_TARGETS = [
  { url: 'http://localhost:8080', label: 'DVWA (localhost:8080)', description: 'Damn Vulnerable Web Application' },
  { url: 'http://localhost:3000', label: 'This App (localhost:3000)', description: 'Test the scanner interface' },
];

function ScanForm({ onScanStart }) {
  const [targetUrl, setTargetUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/scan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ target_url: targetUrl }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to start scan');
      }

      onScanStart(data.scan_id);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const selectDemoTarget = (url) => {
    setTargetUrl(url);
    setError('');
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Hero Section */}
      <div className="text-center space-y-4 mb-12">
        <h2 className="text-4xl md:text-5xl font-bold text-slate-100 tracking-tight">
          Scan for Vulnerabilities
        </h2>
        <p className="text-lg text-slate-400 max-w-2xl mx-auto">
          Automated security testing for common web vulnerabilities including XSS, SQL injection, 
          security headers, and SSL/TLS configuration issues.
        </p>
      </div>

      {/* Main Form Card */}
      <div className="bg-slate-900/50 backdrop-blur-sm border border-cyan-500/20 rounded-2xl p-8 shadow-2xl shadow-cyan-500/10">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="targetUrl" className="block text-sm font-medium text-cyan-400 mb-3 font-mono">
              TARGET URL
            </label>
            <input
              type="text"
              id="targetUrl"
              value={targetUrl}
              onChange={(e) => setTargetUrl(e.target.value)}
              placeholder="http://localhost:8080"
              required
              className="w-full px-4 py-3 bg-slate-950/50 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 transition-all font-mono"
            />
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 flex items-start gap-3 animate-shake">
              <svg className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="text-red-400 text-sm font-medium">Error Starting Scan</p>
                <p className="text-red-400/70 text-sm mt-1">{error}</p>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-slate-950 font-bold py-4 px-6 rounded-lg hover:from-cyan-400 hover:to-blue-400 focus:outline-none focus:ring-4 focus:ring-cyan-500/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 hover:scale-[1.02] active:scale-[0.98]"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Initializing Scan...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                Start Security Scan
              </span>
            )}
          </button>
        </form>
      </div>

      {/* Demo Targets */}
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent"></div>
          <span className="text-sm font-mono text-cyan-400/60">DEMO TARGETS</span>
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent"></div>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          {DEMO_TARGETS.map((target) => (
            <button
              key={target.url}
              onClick={() => selectDemoTarget(target.url)}
              className="bg-slate-900/30 border border-slate-700/50 rounded-xl p-5 text-left hover:border-cyan-500/50 hover:bg-slate-900/50 transition-all group"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-slate-200 font-semibold group-hover:text-cyan-400 transition-colors">
                  {target.label}
                </h3>
                <svg className="w-5 h-5 text-slate-600 group-hover:text-cyan-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </div>
              <p className="text-sm text-slate-500 font-mono">{target.url}</p>
              <p className="text-xs text-slate-600 mt-2">{target.description}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid md:grid-cols-3 gap-4 mt-8">
        {[
          { icon: '🔒', title: 'Security Headers', desc: 'HSTS, CSP, X-Frame-Options' },
          { icon: '🛡️', title: 'Injection Tests', desc: 'XSS & SQL Injection Detection' },
          { icon: '📡', title: 'SSL/TLS Analysis', desc: 'Certificate & Protocol Validation' },
        ].map((item, idx) => (
          <div key={idx} className="bg-slate-900/30 border border-slate-800/50 rounded-lg p-4 text-center">
            <div className="text-3xl mb-2">{item.icon}</div>
            <h3 className="text-slate-200 font-semibold text-sm mb-1">{item.title}</h3>
            <p className="text-slate-500 text-xs">{item.desc}</p>
          </div>
        ))}
      </div>

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-5px); }
          75% { transform: translateX(5px); }
        }
        
        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out;
        }
        
        .animate-shake {
          animation: shake 0.3s ease-in-out;
        }
      `}</style>
    </div>
  );
}

export default ScanForm;
