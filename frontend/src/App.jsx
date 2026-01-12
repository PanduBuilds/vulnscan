import { useState } from 'react';
import ScanForm from './components/ScanForm';
import ScanProgress from './components/ScanProgress';
import ReportView from './components/ReportView';

function App() {
  const [currentView, setCurrentView] = useState('form');
  const [scanId, setScanId] = useState(null);
  const [scanData, setScanData] = useState(null);

  const handleScanStart = (id) => {
    setScanId(id);
    setCurrentView('progress');
  };

  const handleScanComplete = (data) => {
    setScanData(data);
    setCurrentView('report');
  };

  const handleNewScan = () => {
    setScanId(null);
    setScanData(null);
    setCurrentView('form');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Animated background grid */}
      <div className="fixed inset-0 opacity-20">
        <div className="absolute inset-0" style={{
          backgroundImage: `
            linear-gradient(rgba(34, 211, 238, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(34, 211, 238, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
          animation: 'gridMove 20s linear infinite'
        }}></div>
      </div>

      {/* Header */}
      <header className="relative border-b border-cyan-500/20 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-lg flex items-center justify-center shadow-lg shadow-cyan-500/50">
                <svg className="w-7 h-7 text-slate-950" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent tracking-tight">
                  VulnScan
                </h1>
                <p className="text-sm text-cyan-400/60 font-mono">Web Vulnerability Scanner</p>
              </div>
            </div>
            
            <div className="hidden md:flex items-center gap-6 text-sm font-mono">
              <div className="flex items-center gap-2 text-cyan-400/70">
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
                <span>DEMO MODE</span>
              </div>
              <span className="text-slate-500">|</span>
              <span className="text-slate-400">Portfolio Project</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="relative container mx-auto px-6 py-12">
        <div className="max-w-5xl mx-auto">
          {currentView === 'form' && (
            <ScanForm onScanStart={handleScanStart} />
          )}
          
          {currentView === 'progress' && (
            <ScanProgress 
              scanId={scanId} 
              onComplete={handleScanComplete}
              onNewScan={handleNewScan}
            />
          )}
          
          {currentView === 'report' && (
            <ReportView 
              scanData={scanData} 
              onNewScan={handleNewScan}
            />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="relative border-t border-cyan-500/20 mt-20">
        <div className="container mx-auto px-6 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-slate-500">
            <p className="font-mono">
              Built for security research and education
            </p>
            <p className="flex items-center gap-2">
              <span className="text-cyan-400/40">●</span>
              Demo mode: Only localhost/DVWA scanning enabled
            </p>
          </div>
        </div>
      </footer>

      <style>{`
        @keyframes gridMove {
          0% {
            transform: translate(0, 0);
          }
          100% {
            transform: translate(50px, 50px);
          }
        }
      `}</style>
    </div>
  );
}

export default App;
