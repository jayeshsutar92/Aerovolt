import React from 'react';
import { Loader2 } from 'lucide-react';

export interface LoadingStateProps {
  /** Primary loading status message */
  message?: string;
  /** Optional secondary text or hint */
  description?: string;
  /** Size variant for spinner */
  size?: 'sm' | 'md' | 'lg';
  /** Additional container CSS classes */
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading data...',
  description,
  size = 'md',
  className = '',
}) => {
  const sizeMap = {
    sm: 'w-5 h-5',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  const containerPadding = {
    sm: 'py-6',
    md: 'py-12',
    lg: 'py-16',
  };

  return (
    <div
      role="status"
      aria-live="polite"
      className={`flex flex-col items-center justify-center text-center rounded-xl bg-slate-900/40 border border-slate-800/60 p-6 ${containerPadding[size]} ${className}`}
    >
      <div className="relative flex items-center justify-center">
        {/* Ambient Glow */}
        <div className="absolute inset-0 rounded-full bg-cyan-500/20 blur-md animate-pulse" />
        <Loader2 className={`${sizeMap[size]} text-cyan-400 animate-spin relative`} />
      </div>

      {message && (
        <p className="mt-4 text-sm font-medium tracking-wide text-slate-200">
          {message}
        </p>
      )}

      {description && (
        <p className="mt-1 text-xs font-light text-slate-400 max-w-sm">
          {description}
        </p>
      )}

      {/* Screen-reader only announcement */}
      <span className="sr-only">{message}</span>
    </div>
  );
};
