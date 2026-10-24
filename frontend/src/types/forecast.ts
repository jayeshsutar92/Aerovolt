/**
 * Wind generation forecast types matching backend ForecastRecord and ForecastListResponse schemas.
 */

export interface ForecastRecord {
  /** Target delivery start timestamp in UTC (half-hour window start) */
  start_time: string;
  /** Timestamp when the forecast was published by Elexon/NGESO in UTC */
  publish_time: string;
  /** UK electricity settlement date (YYYY-MM-DD) */
  settlement_date: string;
  /** UK half-hourly settlement period (1-48, or 46/50 on clock change days) */
  settlement_period: number;
  /** Forecasted wind generation output in megawatts (MW) */
  generation_mw: number;
  /** Generation fuel type (default: "WIND") */
  fuel_type?: string;
}

export interface ForecastListResponse {
  /** List of wind generation forecast records */
  items: ForecastRecord[];
  /** Total count of records in this response */
  count: number;
  /** Filter settlement date, if specified */
  settlement_date?: string | null;
  /** Fuel type of generation */
  fuel_type: string;
}

export interface ForecastFilterParams {
  /** Settlement date filter (YYYY-MM-DD) */
  settlement_date?: string;
  /** Settlement period filter (1-50) */
  settlement_period?: number;
  /** Purchasing decision cutoff time in ISO format */
  decision_time?: string;
}
