/**
 * Fetch wrapper with baseURL from env.
 *
 * NEXT_PUBLIC_API_URL: used by browser (client-side) — must be public http://localhost:8000
 * API_INTERNAL_URL:    used by Next.js SSR inside Docker — http://backend:8000
 * The internal URL is only available server-side, so we check for it first.
 */
const BASE_URL =
  (typeof window === "undefined"
    ? process.env.API_INTERNAL_URL
    : undefined) ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(status: number, data: unknown) {
    super(`API Error ${status}`);
    this.status = status;
    this.data = data;
  }
}

export async function apiFetch<T = unknown>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (res.status === 204) {
    return undefined as T;
  }

  const data = await res.json();

  if (!res.ok) {
    throw new ApiError(res.status, data);
  }

  return data as T;
}