import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { postIngest } from '../../../../src/lib/api/client'

export const runtime = 'nodejs'

const IngestSchema = z.object({
  filename: z.string().optional(),
  content_type: z.string().optional(),
  s3_uri: z.string().url().optional(),
  tenant_id: z.string().optional(),
})

export async function POST(req: NextRequest) {
  const json = await req.json()
  const parsed = IngestSchema.safeParse(json)
  if (!parsed.success) {
    return NextResponse.json({ error: 'invalid input' }, { status: 400 })
  }
  try {
    const data = await postIngest(parsed.data)
    return NextResponse.json(data, { status: 200 })
  } catch (e) {
    return NextResponse.json({ error: 'upstream error' }, { status: 502, headers: { 'Cache-Control': 'no-store' } })
  }
}
