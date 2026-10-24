/**
 * Accuracy metrics and comparison types matching backend analytics schemas.
 */

export interface AccuracyMetrics {
  /** Mean Absolute Error in megawatts (MW), or null if insufficient pairs */
  mae: number | null;
  /** Root Mean Squared Error in megawatts (MW), or null if insufficient pairs */
  rmse: number | null;
  /** Mean Error / Bias in megawatts (MW). Positive = over-forecast, negative = under-forecast */
  bias: number | null;
  /** Weighted Absolute Percentage Error (%). Null when actual generation is near-zero */
  wape_percent: number | null;
  /** Number of evaluated half-hour intervals */
  sample_count: number;
}

export interface ForecastActualComparisonPoint {
  /** Target delivery start timestamp in UTC */
  start_time: string;
  /** UK electricity settlement date (YYYY-MM-DD) */
  settlement_date: string;
  /** UK half-hourly settlement period (1-50) */
  settlement_period: number;
  /** Actual measured wind generation in megawatts (MW), or null if missing */
  actual_mw: number | null;
  /** Selected forecast wind generation in megawatts (MW), or null if missing */
  forecast_mw: number | null;
  /** Forecast error (forecast_mw - actual_mw) in MW */
  error_mw: number | null;
  /** Absolute error (|forecast_mw - actual_mw|) in MW */
  abs_error_mw: number | null;
}

export interface ComparisonResponse {
  /** Ordered timeseries of aligned comparison data points */
  points: ForecastActualComparisonPoint[];
  /** Summary accuracy evaluation metrics */
  metrics: AccuracyMetrics;
  /** Target settlement date if query was date-scoped */
  settlement_date?: string | null;
  /** Total number of comparison points */
  sample_count: number;
}
