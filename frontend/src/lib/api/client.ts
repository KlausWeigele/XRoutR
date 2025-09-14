import type { paths } from './types'
import { fetchApi } from './fetchApi'

export type IngestResponse = { invoice_id: string; job_id: string }

export async function postIngest(body: Record<string, unknown>) {
  return fetchApi<IngestResponse>('/invoices/ingest', { method: 'POST', body })
}

export async function getValidation(id: string) {
  return fetchApi<{ invoice_id: string; validation: unknown[] }>(`/invoices/${id}/validation`, { method: 'GET' })
}

export async function postRoute(id: string, target: 'datev' = 'datev') {
  return fetchApi<{ invoice_id: string; routed: boolean; target: string }>(`/invoices/${id}/route?target=${target}`, { method: 'POST' })
}
