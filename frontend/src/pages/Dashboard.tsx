import React, { useState, useEffect } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import {
  Wind,
  Calendar,
  Clock,
  ArrowUpRight,
  TrendingUp,
  RefreshCw,
  SlidersHorizontal,
} from 'lucide-react';
import { api, ApiClientError } from '../services/api';
import type { ForecastListResponse, ForecastRecord } from '../types';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';

export const Dashboard: React.FC = () => {
  const [settlementDate, setSettlementDate] = useState<string>('2026-01-01');
  const [selectedPeriod, setSelectedPeriod] = useState<string>('');
  const [data, setData] = useState<ForecastListResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [errorDetails, setErrorDetails] = useState<string | null>(null);

  useEffect(() => {
    let isCurrent = true;

    const loadData = async () => {
      try {
        const periodNum = selectedPeriod ? parseInt(selectedPeriod, 10) : undefined;
        const res = await api.getForecasts({
          settlement_date: settlementDate,
          settlement_period: periodNum,
        });
        if (isCurrent) {
          setData(res);
          setError(null);
          setErrorDetails(null);
          setLoading(false);
        }
      } catch (err) {
        if (isCurrent) {
          if (err instanceof ApiClientError) {
            setError(err.message);
            setErrorDetails(err.code ? `Error Code: ${err.code} (Status: ${err.status})` : null);
          } else {
            setError('An unexpected error occurred while fetching wind forecasts.');
            setErrorDetails(null);
          }
          setData(null);
          setLoading(false);
        }
      }
    };

    void loadData();

    return () => {
      isCurrent = false;
    };
  }, [settlementDate, selectedPeriod]);

  const handleManualRefresh = async () => {
    setLoading(true);
    setError(null);
    setErrorDetails(null);

    try {
      const periodNum = selectedPeriod ? parseInt(selectedPeriod, 10) : undefined;
      const res = await api.getForecasts({
        settlement_date: settlementDate,
        settlement_period: periodNum,
      });
      setData(res);
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err.message);
        setErrorDetails(err.code ? `Error Code: ${err.code} (Status: ${err.status})` : null);
      } else {
        setError('An unexpected error occurred while fetching wind forecasts.');
        setErrorDetails(null);
      }
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  // Format timestamp to concise UTC string
  const formatUtcTime = (isoString: string): string => {
    try {
      const date = new Date(isoString);
      return (
        date.toLocaleTimeString('en-GB', {
          timeZone: 'UTC',
          hour: '2-digit',
          minute: '2-digit',
        }) + ' UTC'
      );
    } catch {
      return isoString;
    }
  };

  // Metrics computation from returned items
  const items: ForecastRecord[] = data?.items || [];
  const peakMw = items.length > 0 ? Math.max(...items.map((i) => i.generation_mw)) : null;
  const minMw = items.length > 0 ? Math.min(...items.map((i) => i.generation_mw)) : null;
  const avgMw =
    items.length > 0
      ? Math.round((items.reduce((sum, i) => sum + i.generation_mw, 0) / items.length) * 10) / 10
      : null;

  // Chart data mapping
  const chartData = items.map((item) => ({
    time: formatUtcTime(item.start_time),
    sp: `SP ${item.settlement_period}`,
    mw: item.generation_mw,
    published: formatUtcTime(item.publish_time),
    rawTime: item.start_time,
  }));

  return (
    <div className="space-y-6">
      {/* Controls Bar */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sm">
        <div className="flex flex-wrap items-center gap-3">
          {/* Date Picker */}
          <div className="flex items-center space-x-2 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/80">
            <Calendar className="w-4 h-4 text-cyan-400" />
            <label htmlFor="settlement-date-input" className="text-xs text-slate-400 font-medium">
              Settlement Date:
            </label>
            <input
              id="settlement-date-input"
              type="date"
              value={settlementDate}
              onChange={(e) => {
                setLoading(true);
                setSettlementDate(e.target.value);
              }}
              className="bg-transparent text-sm text-white font-medium focus:outline-none cursor-pointer"
            />
          </div>

          {/* Period Dropdown */}
          <div className="flex items-center space-x-2 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/80">
            <SlidersHorizontal className="w-4 h-4 text-cyan-400" />
            <label htmlFor="settlement-period-select" className="text-xs text-slate-400 font-medium">
              Period:
            </label>
            <select
              id="settlement-period-select"
              value={selectedPeriod}
              onChange={(e) => {
                setLoading(true);
                setSelectedPeriod(e.target.value);
              }}
              className="bg-transparent text-sm text-white font-medium focus:outline-none cursor-pointer"
            >
              <option value="" className="bg-slate-900 text-white">All Periods (1-48)</option>
              {Array.from({ length: 48 }, (_, i) => i + 1).map((p) => (
                <option key={p} value={p} className="bg-slate-900 text-white">
                  Period {p}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Refresh Action */}
        <button
          type="button"
          onClick={handleManualRefresh}
          disabled={loading}
          className="inline-flex items-center justify-center space-x-2 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-sm font-medium transition-colors shadow-sm shadow-cyan-950 cursor-pointer"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Loading View */}
      {loading && (
        <LoadingState
          message="Retrieving national wind generation forecasts..."
          description={`Fetching settlement date ${settlementDate} from Aerovolt API.`}
          size="lg"
        />
      )}

      {/* Error View */}
      {!loading && error && (
        <ErrorState
          title="Failed to Load Wind Forecasts"
          message={error}
          details={errorDetails ?? undefined}
          onRetry={handleManualRefresh}
          retryLabel="Retry Forecast Request"
        />
      )}

      {/* Empty State View */}
      {!loading && !error && items.length === 0 && (
        <div className="p-12 text-center rounded-xl bg-slate-900/40 border border-slate-800 flex flex-col items-center justify-center">
          <Wind className="w-12 h-12 text-slate-600 mb-3" />
          <h3 className="text-base font-semibold text-slate-300 mb-1">
            No Forecast Records Found
          </h3>
          <p className="text-sm text-slate-500 max-w-sm mb-4">
            No wind generation forecasts are available for date {settlementDate}
            {selectedPeriod ? ` (Period ${selectedPeriod})` : ''}.
          </p>
          <button
            type="button"
            onClick={() => {
              setLoading(true);
              setSettlementDate('2026-01-01');
              setSelectedPeriod('');
            }}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700 transition-colors cursor-pointer"
          >
            Reset Filters to Default (2026-01-01)
          </button>
        </div>
      )}

      {/* Data Loaded View */}
      {!loading && !error && items.length > 0 && (
        <div className="space-y-6">
          {/* Key Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm">
              <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
                <span>Peak Forecast</span>
                <ArrowUpRight className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="mt-2 text-2xl font-bold text-white">
                {peakMw?.toLocaleString()} <span className="text-xs font-normal text-slate-400">MW</span>
              </div>
              <p className="mt-1 text-xs text-slate-500">Highest projected output</p>
            </div>

            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm">
              <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
                <span>Average Forecast</span>
                <TrendingUp className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="mt-2 text-2xl font-bold text-white">
                {avgMw?.toLocaleString()} <span className="text-xs font-normal text-slate-400">MW</span>
              </div>
              <p className="mt-1 text-xs text-slate-500">Mean half-hourly generation</p>
            </div>

            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm">
              <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
                <span>Minimum Forecast</span>
                <Clock className="w-4 h-4 text-blue-400" />
              </div>
              <div className="mt-2 text-2xl font-bold text-white">
                {minMw?.toLocaleString()} <span className="text-xs font-normal text-slate-400">MW</span>
              </div>
              <p className="mt-1 text-xs text-slate-500">Lowest projected output</p>
            </div>

            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm">
              <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
                <span>Forecast Points</span>
                <Wind className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="mt-2 text-2xl font-bold text-white">
                {items.length} <span className="text-xs font-normal text-slate-400">intervals</span>
              </div>
              <p className="mt-1 text-xs text-slate-500">30-min settlement periods</p>
            </div>
          </div>

          {/* Timeseries Visual Chart */}
          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-6">
              <div>
                <h2 className="text-lg font-semibold text-white m-0">
                  Projected Generation Profile
                </h2>
                <p className="text-xs text-slate-400 m-0">
                  Aggregated UK wind generation forecast (MW) across half-hourly delivery windows.
                </p>
              </div>
              <div className="flex items-center space-x-2 text-xs text-slate-400">
                <span className="w-3 h-3 rounded-full bg-cyan-500 inline-block"></span>
                <span>WINDFOR Forecast (MW)</span>
              </div>
            </div>

            <div className="h-72 sm:h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="cyanGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis
                    dataKey="sp"
                    stroke="#64748b"
                    fontSize={11}
                    tickLine={false}
                    axisLine={{ stroke: '#334155' }}
                  />
                  <YAxis
                    stroke="#64748b"
                    fontSize={11}
                    tickLine={false}
                    axisLine={{ stroke: '#334155' }}
                    tickFormatter={(val) => `${val} MW`}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderColor: '#334155',
                      borderRadius: '0.5rem',
                      color: '#f8fafc',
                      fontSize: '0.75rem',
                    }}
                    formatter={(value: unknown) => [
                      typeof value === 'number' ? `${value.toLocaleString()} MW` : String(value),
                      'Forecast',
                    ]}
                    labelFormatter={(label, payload) => {
                      if (payload && payload[0]?.payload) {
                        const p = payload[0].payload;
                        return `${label} (${p.time}) — Published at ${p.published}`;
                      }
                      return label;
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="mw"
                    stroke="#06b6d4"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#cyanGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Forecast Detail Data Table */}
          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm overflow-hidden">
            <h2 className="text-lg font-semibold text-white mb-4">
              Forecast Delivery Schedule
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/60 text-xs uppercase text-slate-400 border-b border-slate-700/80">
                  <tr>
                    <th scope="col" className="px-4 py-3">Settlement Period</th>
                    <th scope="col" className="px-4 py-3">Delivery Start (UTC)</th>
                    <th scope="col" className="px-4 py-3">Published At (UTC)</th>
                    <th scope="col" className="px-4 py-3 text-right">Forecast Generation (MW)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {items.slice(0, 12).map((rec) => (
                    <tr key={`${rec.settlement_date}-${rec.settlement_period}`} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-4 py-3 font-medium text-white">Period {rec.settlement_period}</td>
                      <td className="px-4 py-3 font-mono text-xs">{formatUtcTime(rec.start_time)}</td>
                      <td className="px-4 py-3 font-mono text-xs text-slate-400">{formatUtcTime(rec.publish_time)}</td>
                      <td className="px-4 py-3 text-right font-semibold text-cyan-400">
                        {rec.generation_mw.toLocaleString()} MW
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {items.length > 12 && (
              <p className="mt-3 text-xs text-slate-500 text-center">
                Showing first 12 of {items.length} settlement periods.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
