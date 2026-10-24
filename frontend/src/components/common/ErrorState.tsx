import React from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';

export interface ErrorStateProps {
  /** Optional title for the error alert (defaults to 'Unable to load data') */
  title?: string;
  /** Primary user-facing error message */
  message: string;
  /** Optional technical error details or diagnostic information */
  details?: string;
  /** Optional callback to trigger a retry attempt */
  onRetry?: () => void;
  /** Custom label for retry button (defaults to 'Try Again') */
  retryLabel?: string;
  /** Additional container CSS classes */
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Unable to load data',
  message,
  details,
  onRetry,
  retryLabel = 'Try Again',
  className = '',
}) => {
  return (
    <div
      role="alert"
      className={`flex flex-col items-center justify-center text-center rounded-xl bg-rose-950/20 border border-rose-900/40 p-6 sm:p-10 ${className}`}
    >
      <div className="flex items-center justify-center w-12 h-12 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 mb-4 shadow-sm shadow-rose-950">
        <AlertTriangle className="w-6 h-6" />
      </div>

      <h3 className="text-base font-semibold text-rose-200 m-0">
        {title}
      </h3>

      <p className="mt-2 text-sm text-slate-300 max-w-md m-0">
        {message}
      </p>

      {details && (
        <pre className="mt-3 p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-400 max-w-md overflow-x-auto text-left font-mono">
          {details}
        </pre>
      )}

      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-5 inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 text-sm font-medium transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-rose-500/50 cursor-pointer"
        >
          <RotateCcw className="w-4 h-4 text-slate-400" />
          <span>{retryLabel}</span>
        </button>
      )}
    </div>
  );
};
