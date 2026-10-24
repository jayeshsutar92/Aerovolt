import type {
  ForecastListResponse,
  ForecastFilterParams,
  ComparisonResponse,
  HealthCheckResponse,
  ApiErrorResponse,
} from '../types';

/**
 * Custom error class wrapping backend and network failure details.
 */
export class ApiClientError extends Error {
  public status: number;
  public code?: string;
  public details?: Record<string, unknown>;

  constructor(message: string, status: number = 0, code?: string, details?: Record<string, unknown>) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

/**
 * Base URL resolution: Reads from VITE_API_BASE_URL with localhost:8000 fallback.
 */
const getBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (typeof envUrl === 'string' && envUrl.trim()) {
    return envUrl.trim().replace(/\/+$/, '');
  }
  return 'http://localhost:8000';
};

/**
 * Generic JSON request executor with standardized error extraction.
 */
async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const baseUrl = getBaseUrl();
  const url = `${baseUrl}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
    });
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : 'Unknown network failure';
    throw new ApiClientError(
      `Network connection failed when contacting backend at ${baseUrl}. Ensure the FastAPI server is running. (${errorMsg})`,
      0,
      'NETWORK_ERROR'
    );
  }

  if (!response.ok) {
    let errorCode = `HTTP_${response.status}`;
    let errorMessage = `Request to ${endpoint} failed with status ${response.status} (${response.statusText})`;
    let errorDetails: Record<string, unknown> | undefined;

    try {
      const data = await response.json();
      if (data && typeof data === 'object') {
        // Match standardized Aerovolt ErrorResponse envelope
        if ('error' in data && data.error && typeof data.error === 'object') {
          const apiErr = (data as ApiErrorResponse).error;
          errorCode = apiErr.code || errorCode;
          errorMessage = apiErr.message || errorMessage;
          errorDetails = apiErr.details;
        } else if ('detail' in data) {
          // Default FastAPI HTTPException detail
          errorMessage = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
        }
      }
    } catch {
      // Body is not JSON; keep fallback message
    }

    throw new ApiClientError(errorMessage, response.status, errorCode, errorDetails);
  }

  try {
    return (await response.json()) as T;
  } catch (err) {
    throw new ApiClientError(
      `Invalid JSON payload received from ${endpoint}.`,
      response.status,
      'PARSE_ERROR',
      { originalError: String(err) }
    );
  }
}

/**
 * Aerovolt API Service: typed client functions for backend endpoints.
 */
export const api = {
  /**
   * Fetch backend health status.
   */
  async getHealth(): Promise<HealthCheckResponse> {
    return request<HealthCheckResponse>('/api/health');
  },

  /**
   * Fetch wind generation forecasts.
   * Query params: settlement_date (YYYY-MM-DD), settlement_period (1-50), decision_time.
   */
  async getForecasts(params?: ForecastFilterParams): Promise<ForecastListResponse> {
    const query = new URLSearchParams();
    if (params?.settlement_date) {
      query.append('settlement_date', params.settlement_date);
    }
    if (params?.settlement_period !== undefined) {
      query.append('settlement_period', String(params.settlement_period));
    }
    if (params?.decision_time) {
      query.append('decision_time', params.decision_time);
    }

    const qs = query.toString();
    const endpoint = `/api/forecasts${qs ? `?${qs}` : ''}`;
    return request<ForecastListResponse>(endpoint);
  },

  /**
   * Fetch forecast-versus-actual comparison and accuracy metrics (MAE, RMSE, Bias, WAPE).
   * Query params: settlement_date (YYYY-MM-DD).
   */
  async getAnalytics(settlementDate?: string): Promise<ComparisonResponse> {
    const query = new URLSearchParams();
    if (settlementDate) {
      query.append('settlement_date', settlementDate);
    }

    const qs = query.toString();
    const endpoint = `/api/analytics${qs ? `?${qs}` : ''}`;
    return request<ComparisonResponse>(endpoint);
  },
};
