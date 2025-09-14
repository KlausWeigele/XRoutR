import './globals.css'
import Link from 'next/link'
import { ReactNode } from 'react'

export const metadata = {
  title: 'XRoutR',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="de">
      <body className="min-h-screen flex flex-col">
        <header className="border-b p-4 flex items-center justify-between">
          <nav className="space-x-4">
            <Link href="/inbox">Inbox</Link>
            <Link href="/routing">Routing</Link>
            <Link href="/archive">Archiv</Link>
          </nav>
          <div>
            <select aria-label="Tenant">
              <option>tenant-a</option>
              <option>tenant-b</option>
            </select>
          </div>
        </header>
        <main className="flex-1 p-6">{children}</main>
        <footer className="border-t p-4 text-sm text-gray-600">
          Technische Prüfungen nach EN16931/XRechnung. Keine Rechts-/Steuerberatung.
        </footer>
      </body>
    </html>
  )
}

