import { NextRequest, NextResponse } from 'next/server'
import { getValidation } from '@/src/lib/api/client'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function GET(req: NextRequest, { params }: { params: { id: string } }) {
  // no-store for validation per AGENTS.md §8
  const headers = new Headers({ 'Cache-Control': 'no-store' })
  try {
    const data = await getValidation(params.id)
    return new NextResponse(JSON.stringify(data), { headers, status: 200 })
  } catch (e) {
    return new NextResponse(JSON.stringify({ error: 'upstream error' }), { headers, status: 502 })
  }
}
