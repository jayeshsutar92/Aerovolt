import React from 'react';
import { Navbar, type NavigationPage } from './Navbar';

export interface DashboardLayoutProps {
  /** Page content rendered inside the layout */
  children: React.ReactNode;
  /** Active navigation page highlighted in the Navbar */
  activePage?: NavigationPage;
  /** Callback triggered when a navigation link is clicked */
  onNavigate?: (page: NavigationPage) => void;
  /** Optional page title displayed in the header banner */
  title?: string;
  /** Optional secondary subtitle or description text */
  subtitle?: string;
  /** Optional header action buttons or controls (e.g., date pickers, refresh) */
  actions?: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  activePage = 'dashboard',
  onNavigate,
  title,
  subtitle,
  actions,
}) => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 antialiased selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Top Navigation Bar */}
      <Navbar activePage={activePage} onNavigate={onNavigate} />

      {/* Main Container */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Optional Page Header */}
        {(title || subtitle || actions) && (
          <div className="mb-6 sm:mb-8 pb-4 border-b border-slate-800/80 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              {title && (
                <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white m-0">
                  {title}
                </h1>
              )}
              {subtitle && (
                <p className="mt-1 text-sm text-slate-400 m-0">
                  {subtitle}
                </p>
              )}
            </div>
            {actions && (
              <div className="flex items-center space-x-3 shrink-0">
                {actions}
              </div>
            )}
          </div>
        )}

        {/* Dynamic Page Content */}
        <div className="w-full">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-slate-900 bg-slate-950/80 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p>© {new Date().getFullYear()} Aerovolt — UK Wind Generation Analytics.</p>
          <p>Data sourced from Elexon BMRS (FUELHH & WINDFOR). Timestamps in UTC.</p>
        </div>
      </footer>
    </div>
  );
};
