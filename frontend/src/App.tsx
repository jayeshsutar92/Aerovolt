import { useState } from 'react';
import {
  DashboardLayout,
  LoadingState,
  ErrorState,
  type NavigationPage,
} from './components';
import { RefreshCw, PlayCircle } from 'lucide-react';

function App() {
  const [currentPage, setCurrentPage] = useState<NavigationPage>('dashboard');
  const [simulatedState, setSimulatedState] = useState<'idle' | 'loading' | 'error'>('idle');

  const handleSimulateLoad = () => {
    setSimulatedState('loading');
    setTimeout(() => {
      setSimulatedState('idle');
    }, 1500);
  };

  const handleSimulateError = () => {
    setSimulatedState('error');
  };

  const handleRetry = () => {
    setSimulatedState('loading');
    setTimeout(() => {
      setSimulatedState('idle');
    }, 1200);
  };

  return (
    <DashboardLayout
      activePage={currentPage}
      onNavigate={setCurrentPage}
      title={currentPage === 'dashboard' ? 'National Wind Overview' : 'Forecast Accuracy Analytics'}
      subtitle={
        currentPage === 'dashboard'
          ? 'Live GB electricity settlement outturn and wind generation monitoring.'
          : 'MAE, RMSE, and bias evaluation comparing Elexon WINDFOR against FUELHH actuals.'
      }
      actions={
        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={handleSimulateLoad}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 hover:text-white border border-slate-700 transition-colors cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Test Loading</span>
          </button>
          <button
            type="button"
            onClick={handleSimulateError}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-rose-950/40 hover:bg-rose-900/40 text-xs font-medium text-rose-300 hover:text-rose-100 border border-rose-900/60 transition-colors cursor-pointer"
          >
            <PlayCircle className="w-3.5 h-3.5" />
            <span>Test Error</span>
          </button>
        </div>
      }
    >
      {/* Component Demonstration State Handling */}
      {simulatedState === 'loading' && (
        <LoadingState
          message="Retrieving Elexon BMRS settlement data..."
          description="Fetching half-hourly wind generation records for January 2026."
          size="lg"
        />
      )}

      {simulatedState === 'error' && (
        <ErrorState
          title="Failed to synchronize with Elexon BMRS"
          message="An upstream timeout occurred while requesting the WINDFOR generation forecast dataset."
          details="HTTP 504: Gateway Timeout at https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR"
          onRetry={handleRetry}
          retryLabel="Retry Synchronization"
        />
      )}

      {simulatedState === 'idle' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 rounded-xl bg-slate-900/50 border border-slate-800/80 shadow-sm">
            <h2 className="text-lg font-semibold text-white mb-2">
              {currentPage === 'dashboard' ? 'Wind Generation Outturn' : 'Accuracy Benchmarks'}
            </h2>
            <p className="text-sm text-slate-400 mb-4">
              {currentPage === 'dashboard'
                ? 'Core layout components initialized. Dashboard metrics, timeseries charts, and date filters will mount here in upcoming phases.'
                : 'Comparative analytics metrics (MAE, RMSE, Bias, and WAPE) will be rendered here.'}
            </p>
            <div className="flex items-center space-x-2 text-xs text-cyan-400 font-mono">
              <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
              <span>Layout foundation verified and responsive</span>
            </div>
          </div>

          <div className="p-6 rounded-xl bg-slate-900/50 border border-slate-800/80 shadow-sm">
            <h2 className="text-lg font-semibold text-white mb-2">
              Component Foundation Ready
            </h2>
            <ul className="text-sm text-slate-400 space-y-2">
              <li className="flex items-center space-x-2">
                <span className="text-emerald-400">✓</span>
                <span>Navbar with Aerovolt branding and navigation links</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="text-emerald-400">✓</span>
                <span>DashboardLayout with consistent max-width and header actions</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="text-emerald-400">✓</span>
                <span>Accessible LoadingState with customizable spinner sizes</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="text-emerald-400">✓</span>
                <span>ErrorState with diagnostic details and retry callback</span>
              </li>
            </ul>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}

export default App;
