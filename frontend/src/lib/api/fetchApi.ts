export type FetchApiOptions = {
  method?: string
  body?: any
  headers?: Record<string, string>
  timeoutMs?: number
  retry?: number // only for GET
}

export type FetchApiError = {
  status: number
  code?: number
  message: string
}

export async function fetchApi<T>(path: string, opts: FetchApiOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {}, timeoutMs = 5000, retry = 2 } = opts
  const ctrl = new AbortController()
  const t = setTimeout(() => ctrl.abort(), timeoutMs)
  const urlBase = process.env.BFF_BACKEND_URL || 'http://localhost:8000'

  async function once(): Promise<T> {
    const res = await fetch(urlBase + path, {
      method,
      body: body ? JSON.stringify(body) : undefined,
      headers: { 'content-type': 'application/json', ...headers },
      cache: method === 'GET' ? 'no-store' : undefined,
      signal: ctrl.signal,
    })
    if (!res.ok) {
      let msg = await res.text().catch(() => '')
      const err: FetchApiError = { status: res.status, message: msg || 'API error' }
      throw err
    }
    clearTimeout(t)
    return (await res.json()) as T
  }

  let attempt = 0
  while (true) {
    try {
      return await once()
    } catch (e: any) {
      if (method === 'GET' && attempt < retry && e.status && e.status >= 500) {
        attempt++
        await new Promise((r) => setTimeout(r, 200 * attempt))
        continue
      }
      throw e
    }
  }
}

