export interface ApiErrorPayload {
  code: string;
  message: string;
  details: Record<string, unknown>;
  request_id: string;
}

interface ApiSuccessResponse<T> {
  success: true;
  data: T;
  error: null;
}

interface ApiErrorResponse {
  success: false;
  data: null;
  error: ApiErrorPayload;
}

type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;

export class ApiClientError extends Error {
  status: number;
  code: string;
  details: Record<string, unknown>;
  requestId: string;

  constructor({
    status,
    error,
    fallbackMessage,
  }: {
    status: number;
    error?: Partial<ApiErrorPayload>;
    fallbackMessage: string;
  }) {
    super(error?.message ?? fallbackMessage);
    this.name = "ApiClientError";
    this.status = status;
    this.code = error?.code ?? "UNKNOWN_API_ERROR";
    this.details = error?.details ?? {};
    this.requestId = error?.request_id ?? "";
  }
}

function buildApiPath(path: string) {
  if (path.startsWith("/api")) {
    return path;
  }

  if (path.startsWith("/")) {
    return `/api${path}`;
  }

  return `/api/${path}`;
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(buildApiPath(path), {
    ...init,
    cache: "no-store",
    headers: {
      Accept: "application/json",
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...init?.headers,
    },
  });

  let body: ApiResponse<T> | null = null;

  try {
    body = (await response.json()) as ApiResponse<T>;
  } catch {
    body = null;
  }

  if (!response.ok || !body || body.success !== true) {
    const errorPayload = body && body.success === false ? body.error : undefined;

    throw new ApiClientError({
      status: response.status,
      error: errorPayload,
      fallbackMessage: response.ok
        ? "API response shape is invalid."
        : "Request failed.",
    });
  }

  return body.data;
}
