/**
 * Shared API contracts matching backend common schemas.
 */

export interface ApiErrorDetail {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ApiErrorResponse {
  error: ApiErrorDetail;
}

export interface HealthCheckResponse {
  status: string;
  app: string;
  environment: string;
  version: string;
}
