import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { postRoute } from '../../../../../src/lib/api/client'

export const runtime = 'nodejs'

const Query = z.object({ target: z.enum(['datev']).default('datev') })

export async function POST(req: NextRequest, { params }: { params: { id: string } }) {
  const { searchParams } = new URL(req.url)
  const parsed = Query.safeParse({ target: searchParams.get('target') ?? undefined })
  if (!parsed.success) return NextResponse.json({ error: 'bad target' }, { status: 400, headers: { 'Cache-Control': 'no-store' } })
  try {
    const data = await postRoute(params.id, parsed.data.target)
    return NextResponse.json(data, { headers: { 'Cache-Control': 'no-store' } })
  } catch (e) {
    return NextResponse.json({ error: 'upstream error' }, { status: 502, headers: { 'Cache-Control': 'no-store' } })
  }
}
