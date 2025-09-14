import NextAuth from 'next-auth'
import type { NextAuthOptions } from 'next-auth'

export const runtime = 'nodejs'

const authOptions: NextAuthOptions = {
  providers: [
    // TODO: Add Email (Magic Link) and WebAuthn providers
  ],
  session: { strategy: 'jwt' },
}

const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }

