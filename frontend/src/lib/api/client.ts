import type { paths } from './types'

const BASE = process.env.BFF_BACKEND_URL || 'http://localhost:8000'

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, {
    ...init,
    headers: { 'content-type': 'application/json', ...(init?.headers || {}) },
    cache: 'no-store',
  })
  if (!res.ok) throw new Error(`API error ${res.status}`)
  return (await res.json()) as T
}

export type IngestResponse = { invoice_id: string; job_id: string }

export async function postIngest(body: Record<string, unknown>) {
  return api<IngestResponse>('/invoices/ingest', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function getValidation(id: string) {
  return api<{ invoice_id: string; validation: unknown[] }>(`/invoices/${id}/validation`, {
    method: 'GET',
  })
}

export async function postRoute(id: string, target: 'datev' = 'datev') {
  return api<{ invoice_id: string; routed: boolean; target: string }>(`/invoices/${id}/route?target=${target}`, {
    method: 'POST',
  })
}
