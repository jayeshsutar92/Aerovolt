import React from 'react';
import { Wind, LayoutDashboard, LineChart, Activity } from 'lucide-react';

export type NavigationPage = 'dashboard' | 'analytics';

export interface NavbarProps {
  /** Currently selected page route or tab */
  activePage?: NavigationPage;
  /** Callback invoked when a navigation link is clicked */
  onNavigate?: (page: NavigationPage) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activePage = 'dashboard',
  onNavigate,
}) => {
  const navItems: Array<{ id: NavigationPage; label: string; icon: React.ReactNode }> = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: <LayoutDashboard className="w-4 h-4" />,
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: <LineChart className="w-4 h-4" />,
    },
  ];

  const handleNavClick = (page: NavigationPage, e: React.MouseEvent) => {
    e.preventDefault();
    if (onNavigate) {
      onNavigate(page);
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-900/85 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Title */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/20 text-white">
              <Wind className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  Aerovolt
                </span>
                <span className="hidden sm:inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800/60">
                  GB Grid
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Wind Forecasting & Settlement Analytics
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav aria-label="Primary navigation" className="flex items-center space-x-1 sm:space-x-2">
            {navItems.map((item) => {
              const isActive = activePage === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={(e) => handleNavClick(item.id, e)}
                  aria-current={isActive ? 'page' : undefined}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer ${
                    isActive
                      ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
                  }`}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Status Indicator */}
          <div className="hidden md:flex items-center space-x-2 text-xs font-medium text-slate-400">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="flex items-center space-x-1">
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
              <span>BMRS Live</span>
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
