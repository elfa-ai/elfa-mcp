const DEFAULT_BASE_URL = "https://api.elfa.ai";
const RETRY_DELAY_MS = 1000;

export interface V3ClientOptions {
  apiKey: string;
  baseUrl?: string | undefined;
  timeout: number;
  retries: number;
  headers?: Record<string, string> | undefined;
}

export type V3Params = Record<string, string | number | boolean | string[] | undefined>;

export interface V3Client {
  get(path: string, params?: V3Params): Promise<Record<string, unknown>>;
}

export class V3ApiError extends Error {
  constructor(
    message: string,
    readonly statusCode: number,
  ) {
    super(message);
  }
}

export function queryString(params: V3Params): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined) continue;
    if (Array.isArray(value)) {
      if (value.length > 0) search.set(key, value.join(","));
      continue;
    }
    search.set(key, String(value));
  }
  const text = search.toString();
  return text ? `?${text}` : "";
}

async function errorFrom(response: Response): Promise<V3ApiError> {
  let message = response.statusText || `HTTP ${response.status}`;
  const body = (await response.json().catch(() => null)) as {
    message?: unknown;
    details?: unknown;
  } | null;
  if (typeof body?.message === "string" && body.message) message = body.message;
  if (body?.details !== undefined && body?.details !== null) {
    message += ` ${JSON.stringify(body.details)}`;
  }
  const reset = response.headers.get("RateLimit-Reset");
  if (response.status === 429 && reset) message += `. Resets in ${reset} seconds`;
  return new V3ApiError(message, response.status);
}

function retryable(error: unknown): boolean {
  return !(error instanceof V3ApiError) || error.statusCode >= 500;
}

export function createV3Client(options: V3ClientOptions): V3Client {
  const base = (options.baseUrl ?? DEFAULT_BASE_URL).replace(/\/+$/, "");

  async function once(url: string): Promise<Record<string, unknown>> {
    const response = await fetch(url, {
      headers: {
        ...options.headers,
        Accept: "application/json",
        "x-elfa-api-key": options.apiKey,
      },
      signal: AbortSignal.timeout(options.timeout),
    }).catch((error: unknown) => {
      if (error instanceof Error && error.name === "TimeoutError") {
        throw new Error(`The Elfa API did not answer within ${options.timeout} ms. Retry, or narrow the request.`);
      }
      throw error;
    });
    if (!response.ok) throw await errorFrom(response);
    return (await response.json()) as Record<string, unknown>;
  }

  return {
    async get(path, params = {}) {
      const url = `${base}${path}${queryString(params)}`;
      for (let attempt = 0; ; attempt += 1) {
        try {
          return await once(url);
        } catch (error) {
          if (attempt >= options.retries || !retryable(error)) throw error;
          await new Promise((done) => setTimeout(done, RETRY_DELAY_MS * 2 ** attempt));
        }
      }
    },
  };
}
