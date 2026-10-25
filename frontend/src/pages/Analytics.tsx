import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  BarChart3,
  Calendar,
  RefreshCw,
  Target,
  Scale,
  Percent,
  CheckCircle2,
  AlertCircle,
  Info,
} from 'lucide-react';
import { api, ApiClientError } from '../services/api';
import type { ComparisonResponse, ForecastActualComparisonPoint } from '../types';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';

export const Analytics: React.FC = () => {
  const [settlementDate, setSettlementDate] = useState<string>('2026-01-01');
  const [data, setData] = useState<ComparisonResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [errorDetails, setErrorDetails] = useState<string | null>(null);

  useEffect(() => {
    let isCurrent = true;

    const loadData = async () => {
      try {
        const res = await api.getAnalytics(settlementDate);
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
            setError('An unexpected error occurred while fetching forecast analytics.');
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
  }, [settlementDate]);

  const handleManualRefresh = async () => {
    setLoading(true);
    setError(null);
    setErrorDetails(null);

    try {
      const res = await api.getAnalytics(settlementDate);
      setData(res);
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err.message);
        setErrorDetails(err.code ? `Error Code: ${err.code} (Status: ${err.status})` : null);
      } else {
        setError('An unexpected error occurred while fetching forecast analytics.');
        setErrorDetails(null);
      }
      setData(null);
    } finally {
      setLoading(false);
    }
  };

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

  const points: ForecastActualComparisonPoint[] = data?.points || [];
  const metrics = data?.metrics;

  const chartData = points.map((p) => ({
    sp: `SP ${p.settlement_period}`,
    time: formatUtcTime(p.start_time),
    forecast: p.forecast_mw,
    actual: p.actual_mw,
    error: p.error_mw,
  }));

  return (
    <div className="space-y-6">
      {/* Controls Bar */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/80">
            <Calendar className="w-4 h-4 text-cyan-400" />
            <label htmlFor="analytics-date-input" className="text-[10px] font-medium uppercase tracking-[0.18em] text-slate-400">
              EVALUATION DATE:
            </label>
            <input
              id="analytics-date-input"
              type="date"
              value={settlementDate}
              onChange={(e) => {
                setLoading(true);
                setSettlementDate(e.target.value);
              }}
              className="bg-transparent text-sm font-light text-white focus:outline-none cursor-pointer"
            />
          </div>
        </div>

        <button
          type="button"
          onClick={handleManualRefresh}
          disabled={loading}
          className="inline-flex items-center justify-center space-x-2 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-medium uppercase tracking-[0.14em] transition-colors shadow-sm shadow-cyan-950 cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>REFRESH ANALYSIS</span>
        </button>
      </div>

      {/* Evaluation Coverage Context */}
      <div className="flex items-start sm:items-center space-x-2.5 p-3 rounded-lg bg-slate-900/40 border border-slate-800/80 text-xs font-light text-slate-400">
        <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5 sm:mt-0" />
        <span>
          <strong className="text-slate-300 font-medium">Evaluation Alignment:</strong> Forecasts (WINDFOR) are published at 60-minute resolution (24 intervals) while Actuals (FUELHH) are recorded half-hourly (48 periods). Quantitative metrics (MAE, RMSE, Bias, WAPE) are evaluated over the 24 paired hourly settlement intervals.
        </span>
      </div>

      {/* Loading View */}
      {loading && (
        <LoadingState
          message="Calculating forecast-versus-actual benchmarks..."
          description={`Comparing WINDFOR and FUELHH for ${settlementDate}.`}
          size="lg"
        />
      )}

      {/* Error View */}
      {!loading && error && (
        <ErrorState
          title="Analytics Evaluation Failed"
          message={error}
          details={errorDetails ?? undefined}
          onRetry={handleManualRefresh}
          retryLabel="Retry Evaluation"
        />
      )}

      {/* Empty State View */}
      {!loading && !error && points.length === 0 && (
        <div className="p-12 text-center rounded-xl bg-slate-900/40 border border-slate-800 flex flex-col items-center justify-center">
          <BarChart3 className="w-12 h-12 text-slate-600 mb-3" />
          <h3 className="text-base font-normal tracking-normal text-slate-300 mb-1">
            No Comparison Data Available
          </h3>
          <p className="text-sm font-light text-slate-500 max-w-sm mb-4">
            No overlapping forecast and actual records were identified for settlement date {settlementDate}.
          </p>
          <button
            type="button"
            onClick={() => {
              setLoading(true);
              setSettlementDate('2026-01-01');
            }}
            className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-[11px] font-medium uppercase tracking-[0.14em] text-slate-200 border border-slate-700 transition-colors cursor-pointer"
          >
            RESET TO DEFAULT (2026-01-01)
          </button>
        </div>
      )}

      {/* Data Loaded View */}
      {!loading && !error && points.length > 0 && (
        <div className="space-y-6">
          {/* Quantitative Accuracy Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* MAE */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm">
              <div className="flex items-center justify-between text-slate-400">
                <span className="text-[11px] font-medium uppercase tracking-[0.18em] text-slate-400">MEAN ABSOLUTE ERROR (MAE)</span>
                <Target className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="mt-2 text-3xl sm:text-4xl font-extralight tracking-tight text-white">
                {metrics?.mae !== null && metrics?.mae !== undefined ? (
                  <>
                    {metrics.mae.toLocaleString()}{' '}
                    <span className="text-sm font-light text-slate-400 ml-1">MW</span>
                  </>
                ) : (
                  <span className="text-sm font-light text-slate-500">N/A</span>
                )}
              </div>
              <p className="mt-1 text-xs font-light text-slate-400">Average absolute error magnitude</p>
            </div>

            {/* RMSE */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm">
              <div className="flex items-center justify-between text-slate-400">
                <span className="text-[11px] font-medium uppercase tracking-[0.18em] text-slate-400">ROOT MEAN SQUARED ERROR (RMSE)</span>
                <Scale className="w-4 h-4 text-blue-400" />
              </div>
              <div className="mt-2 text-3xl sm:text-4xl font-extralight tracking-tight text-white">
                {metrics?.rmse !== null && metrics?.rmse !== undefined ? (
                  <>
                    {metrics.rmse.toLocaleString()}{' '}
                    <span className="text-sm font-light text-slate-400 ml-1">MW</span>
                  </>
                ) : (
                  <span className="text-sm font-light text-slate-500">N/A</span>
                )}
              </div>
              <p className="mt-1 text-xs font-light text-slate-400">Penalizes large outlier errors</p>
            </div>

            {/* Mean Bias */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm">
              <div className="flex items-center justify-between text-slate-400">
                <span className="text-[11px] font-medium uppercase tracking-[0.18em] text-slate-400">MEAN BIAS (ME)</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="mt-2 text-3xl sm:text-4xl font-extralight tracking-tight text-white">
                {metrics?.bias !== null && metrics?.bias !== undefined ? (
                  <>
                    {metrics.bias > 0 ? `+${metrics.bias.toLocaleString()}` : metrics.bias.toLocaleString()}{' '}
                    <span className="text-sm font-light text-slate-400 ml-1">MW</span>
                  </>
                ) : (
                  <span className="text-sm font-light text-slate-500">N/A</span>
                )}
              </div>
              <p className="mt-1 text-xs font-light text-slate-400">
                {metrics?.mae !== null && metrics?.bias !== null && metrics?.mae === metrics?.bias
                  ? 'MAE = Bias because forecast exceeded actuals in every interval'
                  : metrics?.bias && metrics.bias > 0
                  ? 'Systematic over-forecasting'
                  : metrics?.bias && metrics.bias < 0
                  ? 'Systematic under-forecasting'
                  : 'Balanced forecast errors'}
              </p>
            </div>

            {/* WAPE / Percentage Metric */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm">
              <div className="flex items-center justify-between text-slate-400">
                <span className="text-[11px] font-medium uppercase tracking-[0.18em] text-slate-400">WAPE (NORMALIZED MAE)</span>
                <Percent className="w-4 h-4 text-purple-400" />
              </div>
              <div className="mt-2 text-3xl sm:text-4xl font-extralight tracking-tight text-white">
                {metrics?.wape_percent !== null && metrics?.wape_percent !== undefined ? (
                  <>{metrics.wape_percent}%</>
                ) : (
                  <span className="text-xs font-light text-slate-500">
                    Suppressed (near-zero actuals)
                  </span>
                )}
              </div>
              <p className="mt-1 text-xs font-light text-slate-400">
                {metrics?.sample_count ?? 0} of 48 periods evaluated (24 hourly pairs)
              </p>
            </div>
          </div>

          {/* Forecast vs Actual Timeseries Chart */}
          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-6">
              <div>
                <h2 className="text-base sm:text-lg font-normal tracking-tight text-white m-0">
                  Forecast vs Actual Generation
                </h2>
                <p className="text-xs font-light text-slate-400 m-0">
                  Direct overlay of procurement forecast against Elexon FUELHH actual generation (MW).
                </p>
              </div>
            </div>

            <div className="h-72 sm:h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
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
                    formatter={(value: unknown, name: unknown) => [
                      typeof value === 'number' ? `${value.toLocaleString()} MW` : 'Missing',
                      name === 'forecast' ? 'Forecast' : 'Actual Outturn',
                    ]}
                    labelFormatter={(label, payload) => {
                      if (payload && payload[0]?.payload) {
                        return `${label} (${payload[0].payload.time})`;
                      }
                      return label;
                    }}
                  />
                  <Legend
                    verticalAlign="top"
                    height={36}
                    wrapperStyle={{ fontSize: '0.75rem' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="forecast"
                    name="Selected Forecast (MW)"
                    stroke="#06b6d4"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    activeDot={{ r: 5 }}
                    connectNulls={true}
                  />
                  <Line
                    type="monotone"
                    dataKey="actual"
                    name="Actual Generation (MW)"
                    stroke="#10b981"
                    strokeWidth={2}
                    dot={{ r: 2 }}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Comparison Table */}
          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm overflow-hidden">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-2">
              <h2 className="text-base sm:text-lg font-normal tracking-tight text-white">
                Settlement Period Comparison Breakdown
              </h2>
              <span className="text-xs font-light text-slate-400">
                All 48 Settlement Periods (30-min intervals)
              </span>
            </div>
            <div className="overflow-x-auto max-h-[520px] overflow-y-auto border border-slate-800/80 rounded-lg">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/95 sticky top-0 border-b border-slate-700/80 backdrop-blur z-10">
                  <tr>
                    <th scope="col" className="px-4 py-3 text-[10px] font-medium uppercase tracking-[0.18em] text-slate-400">PERIOD</th>
                    <th scope="col" className="px-4 py-3 text-[10px] font-medium uppercase tracking-[0.18em] text-slate-400">DELIVERY WINDOW</th>
                    <th scope="col" className="px-4 py-3 text-right text-[10px] font-medium uppercase tracking-[0.18em] text-slate-400">FORECAST (MW)</th>
                    <th scope="col" className="px-4 py-3 text-right text-[10px] font-medium uppercase tracking-[0.18em] text-slate-400">ACTUAL OUTTURN (MW)</th>
                    <th scope="col" className="px-4 py-3 text-right text-[10px] font-medium uppercase tracking-[0.18em] text-slate-400">ERROR (MW)</th>
                    <th scope="col" className="px-4 py-3 text-right text-[10px] font-medium uppercase tracking-[0.18em] text-slate-400">ABS ERROR (MW)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {points.map((pt) => {
                    const isMissing = pt.forecast_mw === null || pt.actual_mw === null;
                    return (
                      <tr
                        key={`${pt.settlement_date}-${pt.settlement_period}`}
                        className="hover:bg-slate-800/30 transition-colors"
                      >
                        <td className="px-4 py-3 font-light text-white">SP {pt.settlement_period}</td>
                        <td className="px-4 py-3 font-mono text-xs font-light text-slate-300">{formatUtcTime(pt.start_time)}</td>
                        <td className="px-4 py-3 text-right">
                          {pt.forecast_mw !== null ? (
                            <span className="font-light text-cyan-400">
                              {pt.forecast_mw.toLocaleString()} MW
                            </span>
                          ) : (
                            <span className="inline-flex items-center text-xs font-light text-amber-400 gap-1 bg-amber-950/20 px-2 py-0.5 rounded border border-amber-900/30">
                              <AlertCircle className="w-3 h-3" /> Absent in WINDFOR
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-right">
                          {pt.actual_mw !== null ? (
                            <span className="font-light text-emerald-400">
                              {pt.actual_mw.toLocaleString()} MW
                            </span>
                          ) : (
                            <span className="inline-flex items-center text-xs font-light text-amber-400 gap-1 bg-amber-950/20 px-2 py-0.5 rounded border border-amber-900/30">
                              <AlertCircle className="w-3 h-3" /> Missing
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-right">
                          {!isMissing && pt.error_mw !== null ? (
                            <span
                              className={`font-mono text-xs font-light ${
                                pt.error_mw > 0
                                  ? 'text-cyan-300'
                                  : pt.error_mw < 0
                                  ? 'text-rose-300'
                                  : 'text-slate-400'
                              }`}
                            >
                              {pt.error_mw > 0 ? `+${pt.error_mw}` : pt.error_mw} MW
                            </span>
                          ) : (
                            <span className="text-slate-600 font-light">—</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-right">
                          {!isMissing && pt.abs_error_mw !== null ? (
                            <span className="font-mono text-xs font-light text-slate-300">
                              {pt.abs_error_mw} MW
                            </span>
                          ) : (
                            <span className="text-slate-600 font-light">—</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <p className="mt-3 text-xs font-light text-slate-500 text-center">
              Displaying all {points.length} settlement periods. Metrics are evaluated over the {metrics?.sample_count ?? 0} periods with paired actuals and WINDFOR forecasts.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
