import Link from 'next/link'

export default function Page() {
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">XRoutR</h1>
      <p>Willkommen. Gehen Sie zur <Link href="/inbox" className="underline">Inbox</Link>.</p>
    </div>
  )
}

